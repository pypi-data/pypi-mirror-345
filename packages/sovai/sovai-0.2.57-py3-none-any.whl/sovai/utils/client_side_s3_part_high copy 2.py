"""
Advanced S3 Partitioned Data Loader (Original Structure - Targeted Fix)

This module provides a high-performance interface for loading partitioned data from S3
with support for ticker and date-based partitioning schemes, parallel loading,
and comprehensive filtering capabilities. Uses explicit year-path discovery
when has_year=True.
"""

from typing import Dict, List, Optional, Union, Any, Tuple, Callable
import pyarrow.dataset as ds
import pyarrow as pa
import pandas as pd
import os
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from functools import lru_cache
from pyarrow.fs import S3FileSystem
import traceback # Import traceback for detailed errors
import pyarrow 

# Try to import custom extensions when available
try:
    # Ensure this import path is correct for your environment
    from sovai.extensions.pandas_extensions import CustomDataFrame
    HAS_CUSTOM_DATAFRAME = True
    print("INFO: CustomDataFrame extension found.") # Use print before logger is guaranteed
except ImportError:
    print("INFO: CustomDataFrame extension not found. Using standard pandas DataFrame.")
    HAS_CUSTOM_DATAFRAME = False
    CustomDataFrame = pd.DataFrame # Define for type hinting

# Ensure authentication module is correctly imported
try:
    # Ensure this import path is correct for your environment
    from sovai.tools.authentication import authentication
    print("INFO: Authentication module loaded.")
except ImportError:
    print("CRITICAL: Failed to import sovai.tools.authentication. S3 access will likely fail.")
    # Define a dummy authentication object or raise an error if critical
    class DummyAuth:
        def get_s3_filesystem_pickle(self, provider, verbose=False):
            print("ERROR: Dummy authentication used. S3 filesystem cannot be obtained.")
            raise NotImplementedError("S3 Authentication module not found.")
    authentication = DummyAuth()

# =========================================================================
# Logging Configuration
# =========================================================================
logger = logging.getLogger(__name__)
logger.propagate = False # Prevent duplicate logs if root logger is configured

if not logger.handlers:
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(name)s:%(funcName)s:%(lineno)d] - %(message)s'
    )

    # File Handler
    try:
        file_handler = logging.FileHandler("data_loader_operations.log", mode='a')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not configure file logging: {e}")

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    logger.setLevel(logging.INFO) # Default level
    logger.info("Logger configured.")
else:
    logger.info("Logger already configured.")


# =========================================================================
# Filesystem Access
# =========================================================================

@lru_cache(maxsize=2)
def get_s3_filesystem(provider: str = "digitalocean") -> Optional[S3FileSystem]:
    """Get cached S3 filesystem for the specified provider."""
    try:
        logger.debug(f"Requesting S3 filesystem for provider: {provider}")
        fs = authentication.get_s3_filesystem_pickle(provider, verbose=False) # Less verbose here
        if fs:
            logger.info(f"Obtained S3 filesystem for provider: {provider}")
            return fs
        else:
            logger.error(f"Authentication module returned None for S3 filesystem (provider: {provider}).")
            return None
    except Exception as e:
        logger.critical(f"Failed to get S3 filesystem for provider {provider}: {e}", exc_info=True)
        return None

# =========================================================================
# Path Management
# =========================================================================

class PathBuilder:
    """Utility class for building and managing S3 data paths."""

    @staticmethod
    def clean_path(path: str) -> str:
        """Remove s3:// prefix if present for consistent path handling."""
        if not path: return ""
        return path.replace('s3://', '')

    # build_ticker_path remains as in original, used by find_ticker_partitions
    @staticmethod
    def build_ticker_path(
        base_path: str,
        ticker: str,
        has_year: bool = True,
        year: Optional[int] = None
    ) -> str:
        """Build a complete ticker-partitioned path."""
        clean_path = PathBuilder.clean_path(base_path)
        ticker_path = f"{clean_path}/ticker_partitioned={ticker}"

        # This logic is now primarily used by find_ticker_partitions again
        if has_year and year is not None:
            # Ensure trailing slash for directory path consistency? Maybe not needed for ds.dataset.
            # Let's match original structure: assume path is .../year=YYYY
             return f"{ticker_path}/year={year}" # Removed trailing slash from original example code for now
            # return f"{ticker_path}/year={year}/" # If trailing slash is needed
        return f"{ticker_path}" # Return base ticker path if no year needed/provided

# =========================================================================
# Partition Discovery (Original Structure)
# =========================================================================

class PartitionFinder:
    """Methods for discovering data partitions in the S3 storage."""

    @staticmethod
    def find_ticker_partitions(
        ticker_base_path: str,
        tickers: List[str],
        has_year: bool = True,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Tuple[str, str]]:
        """
        Find all valid ticker partitions. If has_year=True, finds specific year paths.

        Args:
            ticker_base_path: Base path TO the directory containing ticker_partitioned=...
            tickers: List of tickers to search for.
            has_year: Whether ticker partitions include year=YYYY subdirectories.
            start_year: Optional starting year to filter by (used only if has_year=True).
            end_year: Optional ending year to filter by (used only if has_year=True).

        Returns:
            List of tuples (path_to_load, ticker) for loading.
            If has_year=False, path_to_load is ".../ticker_partitioned=TICKER".
            If has_year=True, path_to_load is ".../ticker_partitioned=TICKER/year=YYYY".
        """
        if not ticker_base_path:
            logger.warning("ticker_base_path is empty in find_ticker_partitions.")
            return []

        fs = get_s3_filesystem()
        if not fs:
            logger.error("Cannot find ticker partitions: S3 filesystem not available.")
            return []

        partitions = []
        clean_ticker_base_path = PathBuilder.clean_path(ticker_base_path)

        logger.info(f"Searching for ticker partitions under s3://{clean_ticker_base_path} "
                    f"for tickers {tickers} (has_year={has_year}, year_range=[{start_year}-{end_year}])")

        for ticker in tickers:
            if not isinstance(ticker, str) or not ticker:
                logger.warning(f"Skipping invalid ticker value: {ticker}")
                continue

            # Path to the directory for this specific ticker
            # e.g., "sovai/.../ticker/ticker/ticker_partitioned=AAPL"
            ticker_partition_base = f"{clean_ticker_base_path}/ticker_partitioned={ticker}"
            s3_ticker_partition_base = f"s3://{ticker_partition_base}" # For logging

            try:
                # Case 1: No year partitioning for this endpoint config
                if not has_year:
                    # We assume the base ticker path exists and add it directly.
                    # DataLoader will handle errors if it doesn't exist.
                    partitions.append((ticker_partition_base, ticker))
                    logger.debug(f"[{ticker}] Added base path (has_year=False): {s3_ticker_partition_base}")
                    continue

                # Case 2: Year partitioning configured for this endpoint
                logger.debug(f"[{ticker}] Extracting years from {s3_ticker_partition_base}...")
                years = PartitionFinder._extract_years(
                    fs, ticker_partition_base, start_year, end_year
                )

                if years:
                    logger.debug(f"[{ticker}] Found years matching filter [{start_year}-{end_year}]: {years}")
                    # Generate specific year paths
                    for year in years:
                        # Use PathBuilder or construct directly
                        # year_path = PathBuilder.build_ticker_path(clean_ticker_base_path, ticker, has_year=True, year=year)
                        year_path = f"{ticker_partition_base}/year={year}"
                        partitions.append((year_path, ticker))
                        logger.debug(f"[{ticker}] Added specific year path: s3://{year_path}")
                else:
                     logger.warning(f"[{ticker}] No year directories found or matched filter [{start_year}-{end_year}] "
                                    f"under {s3_ticker_partition_base} via S3 listing.")
                     # Fallback: If listing failed/returned nothing BUT a year range was specified,
                     # maybe generate the paths anyway? Original code did this. Risky if path doesn't exist.
                     if start_year is not None and end_year is not None:
                         logger.warning(f"[{ticker}] Applying fallback: Generating paths for specified year range {start_year}-{end_year} "
                                        f"despite S3 listing results.")
                         for year in range(start_year, end_year + 1):
                             year_path = f"{ticker_partition_base}/year={year}"
                             partitions.append((year_path, ticker))
                             logger.debug(f"[{ticker}] Added fallback year path: s3://{year_path}")


            except Exception as e:
                # Catch errors during processing for a specific ticker (e.g., fs.ls failed)
                logger.error(f"Error processing ticker '{ticker}' under path '{s3_ticker_partition_base}': {e}", exc_info=True)

        if not partitions:
            logger.warning(f"No partitions generated for tickers {tickers} under s3://{clean_ticker_base_path}. Check paths and data presence.")
        else:
             logger.info(f"Generated {len(partitions)} specific partition paths to load.")

        return partitions

    @staticmethod
    def _extract_years(
        fs: S3FileSystem,
        ticker_path: str, # Path like ".../ticker_partitioned=TICKER"
        start_year: Optional[int],
        end_year: Optional[int]
    ) -> List[int]:
        """
        Extract valid years from subdirectories like 'year=YYYY' under the given ticker path.
        (Original Structure)
        """
        years = []
        s3_ticker_path = f"s3://{ticker_path}" # For logging
        try:
            logger.debug(f"Listing contents of {s3_ticker_path} to find year directories...")
            # Use detail=True to potentially check if items are directories
            listed_items = fs.ls(ticker_path, detail=True)
            logger.debug(f"Found {len(listed_items)} items under {s3_ticker_path}.")

            for item_info in listed_items:
                 # Check if it's a directory (more reliable)
                if item_info.get('type') == pyarrow.fs.FileType.Directory or item_info.get('type') == 'directory':
                    full_path = item_info.get('path') or item_info.get('name')
                    if not full_path: continue

                    basename = os.path.basename(full_path.rstrip('/'))

                    if basename.startswith('year='):
                        year_str = basename.split('=', 1)[1]
                        try:
                            year = int(year_str)
                            # Apply year filtering if needed
                            include = True
                            if start_year is not None and year < start_year:
                                include = False
                            if end_year is not None and year > end_year:
                                include = False

                            if include:
                                years.append(year)
                                logger.debug(f"Found matching year directory: {basename}")
                            #else:
                            #    logger.debug(f"Year directory {basename} outside filter range [{start_year}-{end_year}].")

                        except ValueError:
                            logger.warning(f"Invalid year format in directory name: '{basename}' under {s3_ticker_path}. Skipping.")
                # else:
                #      logger.debug(f"Skipping non-directory item: {item_info.get('name', item_info.get('path'))}")

        except FileNotFoundError:
             logger.warning(f"Path not found during year extraction: {s3_ticker_path}. Cannot extract years.")
             # Return empty list, allows fallback in caller if needed
        except Exception as e:
            # Log errors during S3 list operations
            logger.error(f"Error listing years under {s3_ticker_path}: {e}", exc_info=True)
            # Return empty list, allows fallback in caller if needed

        return sorted(list(set(years))) # Return unique sorted years


    # find_date_partitions remains the same as the original structure
    @staticmethod
    def find_date_partitions(
        date_base_path: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[str]:
        """Find all date partitions within the specified range."""
        # --- Using the same find_date_partitions logic from the previous (PyArrow discovery) version ---
        # --- as it includes better error handling and fallback logic. ---
        date_paths = []
        if not date_base_path:
            logger.warning("date_base_path is empty in find_date_partitions.")
            return date_paths

        fs = get_s3_filesystem()
        if not fs:
            logger.error("Cannot find date partitions: S3 filesystem not available.")
            return date_paths

        clean_path = PathBuilder.clean_path(date_base_path)
        logger.info(f"Searching for date partitions under: s3://{clean_path}")

        try:
            # Date Range Setup
            if start_date and not end_date:
                today = datetime.datetime.now(datetime.timezone.utc).date()
                future_date = today + datetime.timedelta(days=7)
                end_date = future_date.strftime('%Y-%m-%d')
                logger.info(f"Defaulted end_date to: {end_date}")

            start_date_obj = pd.to_datetime(start_date).date() if start_date else None
            end_date_obj = pd.to_datetime(end_date).date() if end_date else None
            if start_date_obj: logger.info(f"Filtering date partitions >= {start_date_obj}")
            if end_date_obj: logger.info(f"Filtering date partitions <= {end_date_obj}")

            # S3 Listing and Filtering
            try:
                listed_items = fs.ls(clean_path, detail=True)
                logger.info(f"S3 list returned {len(listed_items)} items under s3://{clean_path}")

                for item_info in listed_items:
                    if item_info.get('type') == pyarrow.fs.FileType.Directory or item_info.get('type') == 'directory':
                        full_path = item_info.get('path') or item_info.get('name')
                        if not full_path: continue
                        basename = os.path.basename(full_path.rstrip('/'))

                        if basename.startswith('date_partitioned='):
                            try:
                                date_str = basename.split('=', 1)[1]
                                partition_date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

                                include = True
                                if start_date_obj and partition_date_obj < start_date_obj: include = False
                                if end_date_obj and partition_date_obj > end_date_obj: include = False

                                if include:
                                    date_paths.append(full_path)
                                    logger.debug(f"Found matching date partition: s3://{full_path}")

                            except (ValueError, IndexError):
                                logger.warning(f"Invalid date partition format: '{basename}'. Skipping.")
            except FileNotFoundError:
                 logger.error(f"Date partition base path not found: s3://{clean_path}")
            except Exception as e:
                logger.error(f"Error listing S3 partitions under s3://{clean_path}: {e}", exc_info=True)

            # Fallback Path Generation
            if not date_paths and start_date_obj and end_date_obj:
                 logger.warning(f"No date partitions found via listing for s3://{clean_path}. Attempting fallback path generation.")
                 current_dt = start_date_obj
                 while current_dt <= end_date_obj:
                     date_str = current_dt.strftime('%Y-%m-%d')
                     fallback_path = f"{clean_path}/date_partitioned={date_str}"
                     date_paths.append(fallback_path)
                     current_dt += datetime.timedelta(days=1)
                 logger.info(f"Generated {len(date_paths)} fallback date paths.")

        except Exception as e:
            logger.error(f"Unhandled error during date partition discovery for '{date_base_path}': {e}", exc_info=True)

        if not date_paths: logger.warning(f"No date partitions found/generated for: s3://{clean_path}")
        else: logger.info(f"Found {len(date_paths)} date partition paths to load.")
        return date_paths

# =========================================================================
# Data Loading (Targeted Fix in ds.dataset call)
# =========================================================================
class DataLoader:
    """Core data loading functionality with filtering and parallelism."""

    @staticmethod
    def load_partition(
        path: str, # Path to specific partition dir (e.g., .../year=YYYY or .../ticker=TICKER)
        ticker_filter: Optional[List[str]],
        columns: Optional[List[str]],
        start_date: Optional[str],
        end_date: Optional[str]
        # Note: Year filter already applied during path discovery for has_year=True case
    ) -> pd.DataFrame:
        """
        Load and filter data from a single SPECIFIC partition directory.
        Applies date filtering on the 'date' column.
        """
        fs = get_s3_filesystem()
        if not fs:
            logger.error(f"[s3://{path}] Cannot load partition: S3 filesystem not available.")
            return pd.DataFrame()

        s3_path = path if path.startswith('s3://') else f"s3://{path}" # Ensure s3:// prefix
        logger.info(f"--- Loading Partition Start: Specific Path={s3_path} ---")
        logger.debug(f"[{s3_path}] Columns={columns}, DateRange=[{start_date} to {end_date}], PostTickerFilter={ticker_filter}")

        try:
            # --- Create Dataset ---
            # *** KEY CHANGE: Removed partitioning="hive" ***
            # Since 'path' points directly to the directory containing the final parquet file(s)
            # for this specific partition (e.g., .../year=2012/ or .../ticker=AAPL/),
            # we don't need pyarrow to discover partitions from the path itself.
            # It should just read the parquet files within the given directory.
            logger.debug(f"[{s3_path}] Creating pyarrow dataset object (NO explicit partitioning)...")
            try:
                dataset = ds.dataset(s3_path, filesystem=fs, format='parquet')
                logger.info(f"[{s3_path}] Initial dataset schema: {dataset.schema}")
                # No partitioning schema expected here as we didn't ask for discovery based on path
            except pa.lib.ArrowNotFounError: # More specific error
                 logger.error(f"[{s3_path}] S3 path not found.", exc_info=False)
                 logger.info(f"--- Loading Partition Failed (Path Not Found): {s3_path} ---")
                 return pd.DataFrame()
            except Exception as dataset_err:
                 logger.error(f"[{s3_path}] Error creating dataset: {dataset_err}", exc_info=True)
                 logger.info(f"--- Loading Partition Failed (Dataset Creation): {s3_path} ---")
                 return pd.DataFrame()


            # --- Build and Apply Date Filters (on 'date' column) ---
            # This assumes the data *within* the partition file(s) has a 'date' column.
            filters = DataLoader._build_date_filters(start_date, end_date)
            filter_expression = None
            if filters:
                filter_expression = filters[0]
                for f in filters[1:]:
                    filter_expression = filter_expression & f
                logger.debug(f"[{s3_path}] Built date column filter: {filter_expression}")

                try:
                    logger.info(f"[{s3_path}] Applying filter expression: {filter_expression}")
                    filtered_dataset = dataset.filter(filter_expression)
                    logger.info(f"[{s3_path}] Filter applied successfully. Schema after filtering: {filtered_dataset.schema}")
                except pa.lib.ArrowInvalid as filter_err:
                    if "FieldNotFound" in str(filter_err):
                         logger.error(f"[{s3_path}] Error applying filter: 'date' field (or other field in filter) likely not found. "
                                      f"Filter: {filter_expression}. Schema: {dataset.schema}. Error: {filter_err}", exc_info=False)
                    else:
                        logger.error(f"[{s3_path}] ArrowInvalid error applying filter: {filter_expression}. Error: {filter_err}", exc_info=True)
                    logger.info(f"--- Loading Partition Failed (Filter Error): {s3_path} ---")
                    return pd.DataFrame()
                except Exception as filter_e:
                    logger.error(f"[{s3_path}] Unexpected error applying filter {filter_expression}: {filter_e}", exc_info=True)
                    logger.info(f"--- Loading Partition Failed (Filter Error): {s3_path} ---")
                    return pd.DataFrame()
            else:
                logger.info(f"[{s3_path}] No date filters to apply.")
                filtered_dataset = dataset # Use the original dataset if no filters


            # --- Load Data to Arrow Table ---
            logger.info(f"[{s3_path}] Calling dataset.to_table() with columns: {columns or 'ALL'}")
            try:
                table = filtered_dataset.to_table(columns=columns, use_threads=True)
                logger.info(f"[{s3_path}] dataset.to_table() successful. Arrow Table shape: {table.shape}")

                if table.num_rows == 0:
                    logger.warning(f"[{s3_path}] Arrow Table is empty after reading (possibly due to date filter).")

            except pa.lib.ArrowInvalid as to_table_err:
                 if "FieldNotFound" in str(to_table_err) and columns:
                     logger.error(f"[{s3_path}] Error reading table: Column(s) not found. "
                                  f"Requested: {columns}. Schema was: {filtered_dataset.schema}. Error: {to_table_err}", exc_info=False)
                 else:
                    logger.error(f"[{s3_path}] ArrowInvalid error during dataset.to_table(): {to_table_err}", exc_info=True)
                 logger.info(f"--- Loading Partition Failed (to_table ArrowInvalid Error): {s3_path} ---")
                 return pd.DataFrame()
            except Exception as to_table_e:
                logger.error(f"[{s3_path}] Unexpected error during dataset.to_table(): {to_table_e}", exc_info=True)
                logger.info(f"--- Loading Partition Failed (to_table Unexpected Error): {s3_path} ---")
                return pd.DataFrame()

            # --- Convert to Pandas ---
            logger.debug(f"[{s3_path}] Converting Arrow Table to pandas DataFrame...")
            df = table.to_pandas(use_threads=True) # Convert even if empty
            logger.info(f"[{s3_path}] Converted to pandas DataFrame. Shape: {df.shape}")
            logger.debug(f"[{s3_path}] Pandas DataFrame columns: {list(df.columns)}")

            # --- Apply Post-Load Ticker Filter (mainly for date strategy) ---
            if ticker_filter and 'ticker' in df.columns:
                logger.info(f"[{s3_path}] Applying post-load ticker filter: {ticker_filter}")
                initial_rows = len(df)
                valid_ticker_filter = [str(t) for t in ticker_filter if isinstance(t, (str, int, float))]
                df = df[df['ticker'].astype(str).isin(valid_ticker_filter)]
                logger.info(f"[{s3_path}] Post-load ticker filter applied. Rows reduced from {initial_rows} to {len(df)}")
            elif ticker_filter and 'ticker' not in df.columns:
                 logger.warning(f"[{s3_path}] Post-load ticker filter requested but 'ticker' column not found.")

            logger.info(f"--- Loading Partition End: {s3_path} --- Returning DataFrame shape: {df.shape}")
            return df

        except Exception as e:
            # Catch-all for unexpected errors in this function scope
            logger.error(f"[{s3_path}] Unhandled error processing partition: {e}", exc_info=True)
            logger.error(traceback.format_exc())
            logger.info(f"--- Loading Partition Failed (Unhandled Error): {s3_path} ---")
            return pd.DataFrame()

    @staticmethod
    def _build_date_filters(
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> List[ds.Expression]:
        """
        Build PyArrow date filter expressions FOR THE 'date' COLUMN.
        (Original Structure - unchanged)
        """
        filters = []
        try:
            if start_date:
                start_date_obj = pd.to_datetime(start_date).date()
                start_date_pa = pa.scalar(start_date_obj, type=pa.date32()) # Assumes date32
                filters.append(ds.field('date') >= start_date_pa)
            if end_date:
                end_date_obj = pd.to_datetime(end_date).date()
                end_date_pa = pa.scalar(end_date_obj, type=pa.date32()) # Assumes date32
                filters.append(ds.field('date') <= end_date_pa)
        except Exception as e:
             logger.error(f"Failed to build date filters (start={start_date}, end={end_date}): {e}", exc_info=True)
             # Return empty list on error
             return []
        return filters

    # load_data_parallel remains the same as original structure
    @staticmethod
    def load_data_parallel(
        tasks: List[Tuple], # Tuple: (path, ticker_filter, columns, start_date, end_date)
        max_workers: int = 8
    ) -> List[pd.DataFrame]:
        """Process loading tasks in parallel with progress tracking."""
        results = []
        if not tasks:
            logger.warning("load_data_parallel received no tasks.")
            return results

        actual_workers = min(max_workers, len(tasks))
        logger.info(f"Starting parallel load of {len(tasks)} tasks with up to {actual_workers} workers.")

        with ThreadPoolExecutor(max_workers=actual_workers, thread_name_prefix='s3_loader_orig') as executor:
            future_to_info = {} # Map future to path for logging
            for task_tuple in tasks:
                 if not isinstance(task_tuple, tuple) or len(task_tuple) != 5:
                    logger.error(f"Skipping invalid task tuple (expected 5 elements): {task_tuple}")
                    continue
                 # Unpack original task tuple
                 path, ticker_filter, task_columns, task_start_date, task_end_date = task_tuple
                 future = executor.submit(
                    DataLoader.load_partition, # Call the modified load_partition
                    path, ticker_filter, task_columns, task_start_date, task_end_date
                 )
                 future_to_info[future] = path # Store path for context

            for future in tqdm(as_completed(future_to_info), total=len(future_to_info), desc="Loading partitions", unit="partition"):
                path = future_to_info[future]
                log_prefix = f"[Path: s3://{path}]"
                try:
                    df_partition = future.result() # Get result from load_partition
                    if isinstance(df_partition, pd.DataFrame) and not df_partition.empty:
                        logger.debug(f"{log_prefix} Successfully loaded non-empty DataFrame, shape: {df_partition.shape}")
                        results.append(df_partition)
                    elif isinstance(df_partition, pd.DataFrame):
                         logger.info(f"{log_prefix} Loaded empty DataFrame.")
                         # Optionally append empty results.append(df_partition)
                    else:
                         logger.error(f"{log_prefix} Task returned unexpected type: {type(df_partition)}. Skipping.")

                except Exception as e:
                    logger.error(f"{log_prefix} Task failed during result retrieval: {e}", exc_info=True)

        logger.info(f"Parallel loading finished. Collected {len(results)} non-empty DataFrames.")
        return results

# =========================================================================
# Main Loading Interface (Original Structure)
# =========================================================================

# _get_year_range remains the same as original structure
def _get_year_range(
    start_date: Optional[str],
    end_date: Optional[str]
) -> Tuple[Optional[int], Optional[int]]:
    """Determine year range from date strings."""
    start_year = None
    end_year = None
    try:
        if start_date: start_year = pd.to_datetime(start_date).year
        if end_date: end_year = pd.to_datetime(end_date).year
        elif start_year: # Default end year if only start date given
            end_year = datetime.datetime.now().year + 1 # Match original logic
            logger.info(f"Using default end year: {end_year} (current year + 1)")
    except ValueError as e:
         logger.warning(f"Invalid date format in _get_year_range ('{start_date}', '{end_date}'): {e}")
    if start_year is not None and end_year is not None and start_year > end_year:
        logger.warning(f"Start year {start_year} > end year {end_year}. Adjusting end year.")
        end_year = start_year
    return start_year, end_year

# load_data remains the same as original structure
def load_data(
    ticker_path: str = '',
    date_path: str = '',
    has_year: bool = True,
    tickers: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    columns: Optional[List[str]] = None,
    max_workers: int = 8,
    post_process: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None
) -> pd.DataFrame:
    """Load data from S3 using original partition discovery and loading logic."""
    tasks = [] # Task tuple: (path, ticker_filter, columns, start_date, end_date)

    # --- Date Range and Year Filter Setup (for PartitionFinder) ---
    effective_end_date = end_date
    if start_date and not end_date:
        today = datetime.datetime.now(datetime.timezone.utc).date()
        future_date = today + datetime.timedelta(days=7)
        effective_end_date = future_date.strftime('%Y-%m-%d')
        logger.info(f"Defaulted end_date to {effective_end_date}.")

    filter_start_year, filter_end_year = _get_year_range(start_date, effective_end_date)

    logger.info(f"Loading data with parameters: ticker_path='s3://{ticker_path}', date_path='s3://{date_path}', "
               f"has_year={has_year}, tickers={tickers}, start_date={start_date}, end_date={effective_end_date}, columns={columns}")

    # --- Determine Loading Strategy & Generate Tasks (Original Logic) ---
    use_ticker_strategy = bool(tickers and ticker_path)
    use_date_strategy = bool(date_path and not use_ticker_strategy)

    if use_ticker_strategy:
        logger.info(f"Strategy: Using Ticker Partitioning (has_year={has_year}). Discovering specific partitions...")
        # Calls original find_ticker_partitions which uses _extract_years if has_year=True
        ticker_partitions = PartitionFinder.find_ticker_partitions(
            ticker_path,
            tickers,
            has_year,
            filter_start_year, # Pass year range for discovery
            filter_end_year
        )

        for path, ticker in ticker_partitions:
            # Original task tuple structure
            tasks.append((path, [ticker], columns, start_date, effective_end_date))

        logger.info(f"Added {len(tasks)} ticker-based loading tasks (specific paths generated).")

    elif use_date_strategy:
        logger.info(f"Strategy: Using Date Partitioning. Discovering specific partitions...")
        date_partitions = PartitionFinder.find_date_partitions(date_path, start_date, effective_end_date)

        for path in date_partitions:
             # Original task tuple structure, ticker filter passed for post-load filtering
            tasks.append((path, tickers, columns, start_date, effective_end_date))

        logger.info(f"Added {len(tasks)} date-based loading tasks.")

    # --- Execute Tasks and Process Results ---
    if not tasks:
        logger.warning("No loading tasks generated.")
        return CustomDataFrame() if HAS_CUSTOM_DATAFRAME else pd.DataFrame()

    loaded_dfs = DataLoader.load_data_parallel(tasks, max_workers)

    if loaded_dfs:
        logger.info(f"Concatenating results from {len(loaded_dfs)} partitions...")
        try:
            # Use sort=False for potential performance improvement if order isn't critical before explicit sort
            final_df = pd.concat(loaded_dfs, ignore_index=True, sort=False)
            logger.info(f"Concatenated data shape: {final_df.shape}")

            # Optional Sort
            sort_cols = [col for col in ['ticker', 'date'] if col in final_df.columns]
            if sort_cols:
                logger.info(f"Sorting final DataFrame by {sort_cols}...")
                try:
                    final_df = final_df.sort_values(by=sort_cols, kind='mergesort').reset_index(drop=True)
                except Exception as sort_err:
                     logger.warning(f"Failed to sort final DataFrame: {sort_err}.", exc_info=False)

            # Optional Post-processing
            if post_process and callable(post_process):
                logger.info("Applying post-processing function...")
                try:
                    final_df = post_process(final_df)
                    logger.info(f"Post-processing complete. Shape: {final_df.shape}")
                except Exception as pp_err:
                     logger.error(f"Error during post-processing: {pp_err}", exc_info=True)

            # Final return
            return CustomDataFrame(final_df) if HAS_CUSTOM_DATAFRAME else final_df

        except Exception as concat_err:
             logger.error(f"Error during final concatenation/processing: {concat_err}", exc_info=True)
             return CustomDataFrame() if HAS_CUSTOM_DATAFRAME else pd.DataFrame() # Return empty on error
    else:
        logger.warning("No data loaded from any partition.")
        return CustomDataFrame() if HAS_CUSTOM_DATAFRAME else pd.DataFrame() # Return empty


# =========================================================================
# Endpoint Configuration (Remains the Same)
# =========================================================================
ENDPOINT_CONFIG = {
    "patents/applications": {
        "ticker_path": "sovai/sovai-patents-bulk/applications/ticker/ticker",
        "date_path": "sovai/sovai-patents-bulk/applications/date/date",
        "has_year": True
    },
    "patents/grants": {
        "ticker_path": "sovai/sovai-patents-bulk/grants/ticker/ticker",
        "date_path": "sovai/sovai-patents-bulk/grants/date/date",
        "has_year": True
    },
    "clinical/trials": {
        "ticker_path": "sovai/sovai-clinical-trials-export/partitioned/ticker/ticker",
        "date_path": "sovai/sovai-clinical-trials-export/partitioned/date/date",
        "has_year": False
    },
    # ... (rest of ENDPOINT_CONFIG remains the same as provided in your original script) ...
     "spending/awards": {
        "ticker_path": "sovai/sovai-government/partitioned/awards/ticker",
        "date_path": "sovai/sovai-government/partitioned/awards/date",
        "has_year": False
    },
    "spending/compensation": {
        "ticker_path": "sovai/sovai-government/partitioned/compensation/ticker",
        "date_path": "sovai/sovai-government/partitioned/compensation/date",
        "has_year": False
    },
    "spending/competition": {
        "ticker_path": "sovai/sovai-government/partitioned/competition/ticker",
        "date_path": "sovai/sovai-government/partitioned/competition/date",
        "has_year": False
    },
    "spending/contracts": {
        "ticker_path": "sovai/sovai-government/partitioned/contract/ticker",
        "date_path": "sovai/sovai-government/partitioned/contract/date",
        "has_year": False
    },
    "spending/product": {
        "ticker_path": "sovai/sovai-government/partitioned/product/ticker",
        "date_path": "sovai/sovai-government/partitioned/product/date",
        "has_year": False
    },
    "spending/transactions": {
        "ticker_path": "sovai/sovai-government/partitioned/transactions/ticker",
        "date_path": "sovai/sovai-government/partitioned/transactions/date",
        "has_year": False
    },
    "spending/entities": {
        "ticker_path": "sovai/sovai-government/partitioned/entities/ticker",
        "date_path": "",
        "has_year": False
    },
    "spending/location": {
        "ticker_path": "sovai/sovai-government/partitioned/location/ticker",
         "date_path": "",
        "has_year": False
    },
    "lobbying": {
        "ticker_path": "sovai/sovai-lobbying/partitioned/ticker",
        "date_path": "sovai/sovai-lobbying/partitioned/date",
        "has_year": False
    },
    "accounting/weekly": {
        "ticker_path": "sovai/sovai-accounting/partitioned/ticker",
        "date_path": "sovai/sovai-accounting/partitioned/date",
        "has_year": False
    },
    "ratios/normal": {
        "ticker_path": "sovai/sovai-ratios/partitioned/ticker",
        "date_path": "sovai/sovai-ratios/partitioned/date",
        "has_year": False
    },
    "complaints/public": {
        "ticker_path": "sovai/sovai-complaints/partitioned/ticker",
        "date_path": "sovai/sovai-complaints/partitioned/date",
        "has_year": False
    },
    "factors/accounting": {
        "ticker_path": "sovai/sovai-factors/accounting/partitioned/ticker",
        "date_path": "sovai/sovai-factors/accounting/partitioned/date",
        "has_year": False
    },
    "factors/alternative": {
        "ticker_path": "sovai/sovai-factors/alternative/partitioned/ticker",
        "date_path": "sovai/sovai-factors/alternative/partitioned/date",
        "has_year": False
    },
    "factors/comprehensive": {
        "ticker_path": "sovai/sovai-factors/comprehensive/partitioned/ticker",
        "date_path": "sovai/sovai-factors/comprehensive/partitioned/date",
        "has_year": False
    },
    "factors/coefficients": {
        "ticker_path": "sovai/sovai-factors/coefficients/partitioned/ticker",
        "date_path": "sovai/sovai-factors/coefficients/partitioned/date",
        "has_year": False
    },
    "factors/standard_errors": {
        "ticker_path": "sovai/sovai-factors/standard_errors/partitioned/ticker",
        "date_path": "sovai/sovai-factors/standard_errors/partitioned/date", # Corrected path?
        "has_year": False
    },
    "factors/t_statistics": {
        "ticker_path": "sovai/sovai-factors/t_statistics/partitioned/ticker",
        "date_path": "sovai/sovai-factors/t_statistics/partitioned/date",
        "has_year": False
    },
    "factors/model_metrics": {
        "ticker_path": "sovai/sovai-factors/model_metrics/partitioned/ticker",
        "date_path": "sovai/sovai-factors/model_metrics/partitioned/date",
        "has_year": False
    },
    "breakout": {
        "ticker_path": "sovai/sovai-breakout-price/partitioned/ticker",
        "date_path": "sovai/sovai-breakout-price/partitioned/date",
        "has_year": False
    },
    "visas/h1b": {
        "ticker_path": "sovai/sovai-employment/partitioned/ticker",
        "date_path": "sovai/sovai-employment/partitioned/date",
        "has_year": False
    },
    "wikipedia/views": {
        "ticker_path": "sovai/sovai-wiki/views/partitioned/ticker",
        "date_path": "sovai/sovai-wiki/views/partitioned/date",
        "has_year": False
    },
    "insider/trading": {
        "ticker_path": "sovai/sovai-insider/partitioned/ticker",
        "date_path": "sovai/sovai-insider/partitioned/date",
        "has_year": False
    },
    "corprisk/risks": {
        "ticker_path": "sovai/sovai-flags/risks/partitioned/ticker",
        "date_path": "sovai/sovai-flags/risks/partitioned/date",
        "has_year": False
    },
    "corprisk/accounting": {
        "ticker_path": "sovai/sovai-flags/accounting/partitioned/ticker",
        "date_path": "sovai/sovai-flags/accounting/partitioned/date",
        "has_year": False
    },
    "corprisk/events": {
        "ticker_path": "sovai/sovai-flags/events/partitioned/ticker",
        "date_path": "sovai/sovai-flags/events/partitioned/date",
        "has_year": False
    },
    "corprisk/misstatements": {
        "ticker_path": "sovai/sovai-flags/misstatements/partitioned/ticker",
        "date_path": "sovai/sovai-flags/misstatements/partitioned/date",
        "has_year": False
    },
    "short/volume": {
        "ticker_path": "sovai/sovai-short/short_volume_weekly/partitioned/ticker",
        "date_path": "sovai/sovai-short/short_volume_weekly/partitioned/date",
        "has_year": False
    },
    "short/maker": {
        "ticker_path": "sovai/sovai-short/over_shorted/partitioned/ticker",
        "date_path": "sovai/sovai-short/over_shorted/partitioned/date",
        "has_year": False
    },
    "short/over_shorted": {
        "ticker_path": "sovai/sovai-short/over_shorted/partitioned/ticker",
        "date_path": "sovai/sovai-short/over_shorted/partitioned/date",
        "has_year": False
    },
    "institutional/trading": {
        "ticker_path": "sovai/sovai-institutional/trading/partitioned/ticker",
        "date_path": "sovai/sovai-institutional/trading/partitioned/date",
        "has_year": False
    },
}

# =========================================================================
# Public Interface (Original Structure - input handling slightly improved)
# =========================================================================

def load_frame_s3_partitioned_high(
    endpoint: str,
    tickers: Optional[Union[str, List[str]]] = None,
    columns: Optional[Union[str, List[str]]] = None, # Accept string or list for columns
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    post_process: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
    max_workers: int = 8 # Allow setting workers
) -> pd.DataFrame: # Return type hint
    """Load data for the specified endpoint using original partition discovery."""
    if endpoint not in ENDPOINT_CONFIG:
        available = ", ".join(sorted(ENDPOINT_CONFIG.keys()))
        raise ValueError(f"Invalid endpoint: '{endpoint}'. Available endpoints: {available}")

    config = ENDPOINT_CONFIG[endpoint]
    logger.info(f"--- Starting data load [Original Structure] for endpoint: '{endpoint}' ---")
    logger.info(f"Raw Parameters: tickers={type(tickers)}, columns={type(columns)}, "
                f"start_date={start_date}, end_date={end_date}, max_workers={max_workers}")

    # --- Input Parameter Processing ---
    processed_tickers: Optional[List[str]] = None
    if tickers:
        if isinstance(tickers, str):
            processed_tickers = [t.strip() for t in tickers.split(',') if t.strip()]
        elif isinstance(tickers, list):
            processed_tickers = [str(t).strip() for t in tickers if str(t).strip()]
        else:
            logger.warning(f"Tickers type unexpected ({type(tickers)}). Attempting conversion.")
            try: processed_tickers = [str(tickers).strip()]
            except: processed_tickers = None
        if not processed_tickers: processed_tickers = None # Ensure None if empty list resulted
    logger.debug(f"Processed tickers: {processed_tickers}")

    processed_columns: Optional[List[str]] = None
    if columns:
        if isinstance(columns, str):
            processed_columns = [c.strip() for c in columns.split(',') if c.strip()]
        elif isinstance(columns, list):
            processed_columns = [str(c).strip() for c in columns if str(c).strip()]
        else:
             logger.warning(f"Columns type unexpected ({type(columns)}). Attempting conversion.")
             try: processed_columns = [str(columns).strip()]
             except: processed_columns = None
        if not processed_columns: processed_columns = None # Treat empty as None (load all)
    logger.debug(f"Processed columns: {processed_columns} (None means load all)")


    # --- Get Endpoint Config ---
    ticker_path = config.get("ticker_path", "")
    date_path = config.get("date_path", "")
    has_year = config.get("has_year", False)

    logger.info(f"Endpoint config: ticker_path='s3://{ticker_path}', date_path='s3://{date_path}', has_year={has_year}")

    # --- Path Validation (Basic) ---
    if processed_tickers and not ticker_path:
         logger.error(f"Ticker filter requested but endpoint '{endpoint}' has no 'ticker_path'.")
         return CustomDataFrame() if HAS_CUSTOM_DATAFRAME else pd.DataFrame()
    if (start_date or end_date) and not processed_tickers and not date_path:
         logger.error(f"Date filter requested without tickers for endpoint '{endpoint}', but no 'date_path'.")
         return CustomDataFrame() if HAS_CUSTOM_DATAFRAME else pd.DataFrame()

    # --- Call Core Loading Logic (Original Structure) ---
    try:
        df = load_data(
            ticker_path=ticker_path,
            date_path=date_path,
            has_year=has_year, # Passed to find_ticker_partitions
            tickers=processed_tickers,
            start_date=start_date,
            end_date=end_date, # Pass original end_date, load_data handles default
            columns=processed_columns,
            max_workers=max_workers,
            post_process=post_process
        )
        logger.info(f"--- Data load [Original Structure] finished for '{endpoint}'. Shape: {df.shape} ---")
        return df # Already DataFrame or CustomDataFrame from load_data

    except Exception as e:
        logger.critical(f"Core data loading failed for endpoint '{endpoint}': {e}", exc_info=True)
        logger.error(traceback.format_exc())
        return CustomDataFrame() if HAS_CUSTOM_DATAFRAME else pd.DataFrame()

# =========================================================================
# Example Usage (Copied from previous version for testing convenience)
# =========================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)
    logger.info("Running example usage [Original Structure Version]...")

    # --- Example 1: has_year=True ---
    try:
        logger.info("\n--- Example 1: patents/applications (has_year=True) ---")
        df_patents = load_frame_s3_partitioned_high(
            endpoint="patents/applications",
            tickers=["000020.KS"], # Ensure this ticker and year exist
            start_date="2012-01-01",
            end_date="2012-12-31",
            columns="publication_number,title",
            max_workers=4
        )
        logger.info(f"Example 1 Result Shape: {df_patents.shape}")
        if not df_patents.empty: logger.info("Example 1 Head:\n%s", df_patents.head())
        else: logger.warning("Example 1 empty. Check S3 path, data, date, ticker, year=2012 existence, credentials.")
    except Exception as e: logger.error(f"Example 1 failed: {e}", exc_info=True)

    # --- Example 2: has_year=False ---
    try:
        logger.info("\n--- Example 2: clinical/trials (has_year=False) ---")
        df_trials = load_frame_s3_partitioned_high(
            endpoint="clinical/trials",
            tickers=["PFE", "AMGN"], # Placeholder tickers
            columns=["nct_id", "brief_title", "overall_status"],
            max_workers=4
        )
        logger.info(f"Example 2 Result Shape: {df_trials.shape}")
        if not df_trials.empty: logger.info("Example 2 Head:\n%s", df_trials.head())
        else: logger.warning("Example 2 empty. Check S3 path, data, tickers, credentials.")
    except Exception as e: logger.error(f"Example 2 failed: {e}", exc_info=True)

    # --- Example 3: Date Range only ---
    try:
        logger.info("\n--- Example 3: Date-only query (spending/awards) ---")
        df_spending = load_frame_s3_partitioned_high(
            endpoint="spending/awards",
            tickers=None,
            start_date="2023-01-01", # Adjust date range as needed
            end_date="2023-01-31",
            max_workers=4
        )
        logger.info(f"Example 3 Result Shape: {df_spending.shape}")
        if not df_spending.empty: logger.info("Example 3 Head:\n%s", df_spending.head())
        else: logger.warning("Example 3 empty. Check S3 path, data, date range, credentials.")
    except Exception as e: logger.error(f"Example 3 failed: {e}", exc_info=True)

    logger.info("\n--- Example Usage [Original Structure Version] Finished ---")