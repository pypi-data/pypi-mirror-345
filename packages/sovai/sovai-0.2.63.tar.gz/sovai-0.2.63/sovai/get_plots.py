# Inside plot/get_plot.py

from .plots.bankruptcy.bankruptcy_plots import *
from .plots.breakout.breakout_plots import *
from .plots.accounting.accounting_plots import *
from .plots.ratios.ratios_plots import *
from .plots.institutional.institutional_plots import *
from .plots.news.news_plots import plot_news_daily, create_plot_news_sent_price, plot_above_sentiment_returns, run_dash_news_ts
from .plots.corp_risk.corp_risk_plots import *

from .plots.insider.insider_plots import *
from .plots.allocation.allocation_plots import *
from .plots.earnings_surprise.earnings_surprise_plots import *

from sovai.utils.plot import plotting_data
from typing import Optional, Union, Tuple, List, Dict
from sovai import data
from IPython.display import Markdown, display
import plotly.io as pio
import pandas as pd

# Changing the default plotting backend to Plotly
pd.options.plotting.backend = "plotly"
pd.set_option("display.max_columns", None)

# Setting the default theme for Plotly to a dark mode
pio.templates.default = "plotly_dark"


def enable_plotly_in_cell():
    import IPython
    from plotly.offline import init_notebook_mode

    display(
        IPython.core.display.HTML(
            """<script src="/static/components/requirejs/require.js"></script>"""
        )
    )
    init_notebook_mode(connected=False)


def _draw_graphs(data: Union[Dict, List[Dict]]):
    # print(data)
    if isinstance(data, list):
        for plot in data:
            for _, val in plot.items():
                return plotting_data(val)
                break
    else:
        for _, val in data.items():
            return plotting_data(val)
            


from typing import Optional, Union, Tuple, List, Dict

# Assuming other necessary imports and definitions here
def generate_error_message(analysis_type, chart_type, source, verbose):
    if source == "local":
        code_snippet = (
            f"dataset = sov.data('{analysis_type}/monthly')\n"
            f"sov.plot('{analysis_type}', chart_type='{chart_type}', df=dataset)"
        )
        message = (
            f"**Dataset is empty.** Will fetch the data on your behalf:\n\n"
            f"```python\n{code_snippet}\n```"
        )
        if verbose:
            print(display(Markdown(message)))
        return ""
    else:
        display(Markdown("**An unknown error occurred.**"))

## 

plot_ticker_widget

PLOT_FUNCTION_MAPPER = {
    ("breakout", "predictions", "local", True): get_predict_breakout_plot_for_ticker,
    ("breakout", "accuracy", "local", True): interactive_plot_display_breakout_accuracy,
    ("accounting", "balance", "local", False): get_balance_sheet_tree_plot_for_ticker,
    ("accounting", "cashflows", "local", True): plot_cash_flows,
    ("accounting", "assets", "local", True): plot_assets,  # full_history=False
    ("ratios", "relative", "local", True): plot_ratios_triple,
    ("ratios", "benchmark", "local", True): plot_ratios_benchmark,
    ("institutional", "flows", "local", True): institutional_flows_plot,
    ("institutional", "prediction", "local", True): institutional_flow_predictions_plot,
    ("insider", "percentile", "local", True): create_parallel_coordinates_plot_single_ticker,
    ("insider", "flows", "local", True): insider_flows_plot,
    ("insider", "prediction", "local", True): insider_flow_predictions_plot,
    ("news", "sentiment", "local", True): plot_above_sentiment_returns,
    ("news", "strategy", "local", True): plot_news_daily,
    ("news", "analysis", "local", True): run_dash_news_ts,
    ("corprisk/risks", "line", "local", True): plotting_corp_risk_line,
    ("allocation", "line", "local", True): create_line_plot_allocation,
    ("allocation", "stacked", "local", True): create_stacked_bar_plot_allocation,
    ("earnings", "line", "local", True): create_earnings_surprise_plot,
    ("earnings", "tree", "local", True): earnings_tree,
    ("bankruptcy", "compare", "local", True): plot_bankruptcy_monthly_line,
    ("bankruptcy", "pca_clusters", "local", True): plot_pca_clusters,
    ("bankruptcy", "predictions", "local", True): plot_ticker_widget,
    ("bankruptcy", "shapley", "database"): _draw_graphs,
    ("bankruptcy", "pca", "database"): _draw_graphs,
    ("bankruptcy", "line", "database"): _draw_graphs,
    ("bankruptcy", "similar", "database"): _draw_graphs,
    ("bankruptcy", "facet", "database"): _draw_graphs,
    ("bankruptcy", "shapley", "database"): _draw_graphs,
    ("bankruptcy", "stack", "database"): _draw_graphs,
    ("bankruptcy", "box", "database"): _draw_graphs,
    ("bankruptcy", "waterfall", "database"): _draw_graphs,
    ("bankruptcy", "pca_relation", "database"): _draw_graphs,
    ("bankruptcy", "line_relation", "database"): _draw_graphs,
    ("bankruptcy", "facet_relation", "database"): _draw_graphs,
    ("bankruptcy", "time_global", "database"): _draw_graphs,
    ("bankruptcy", "stack_global", "database"): _draw_graphs,
    ("bankruptcy", "box_global", "database"): _draw_graphs,
    ("bankruptcy", "waterfall_global", "database"): _draw_graphs,
    ("bankruptcy", "confusion_global", "database"): _draw_graphs,
    ("bankruptcy", "classification_global", "database"): _draw_graphs,
    ("bankruptcy", "precision_global", "database"): _draw_graphs,
    ("bankruptcy", "lift_global", "database"): _draw_graphs,




    # Add other mappings as needed
}


def plot(
    dataset_name,
    chart_type=None,
    df=None,
    tickers: Optional[List[str]] = None,
    ticker: Optional[List[str]] = None,
    verbose=False,
    purge_cache=False,
    **kwargs,
):
    # Enable plotly in cell
    enable_plotly_in_cell()

    # Default values
    plot_function = None
    full_history = None  # Set to None initially, as it only applies to local sources

    # Loop to find the plot function key based on dataset_name, chart_type, and source
    for key in PLOT_FUNCTION_MAPPER:
        if len(key) == 4 and key[:3] == (dataset_name, chart_type, "local"):
            # Local source with full_history value in the key
            _, _, source, full_history = key
            plot_function = PLOT_FUNCTION_MAPPER.get(key)
            break
        elif len(key) == 3 and key[:3] == (dataset_name, chart_type, "database"):
            # Database source, full_history is not relevant
            _, _, source = key
            plot_function = PLOT_FUNCTION_MAPPER.get(key)
            break

    # If no valid plot function is found, raise an error
    if plot_function is None:
        raise ValueError(
            f"Plotting function for {dataset_name} with chart type {chart_type} not found."
        )

    # If source is local, handle the local data case
    if source == "local":
        try:
            if df is None:  # Check if the DataFrame is None
                add_text = generate_error_message(
                    dataset_name, chart_type, source, verbose
                )
                # First attempt: Call plot_function with tickers or ticker
                try:
                    return plot_function(
                        data(dataset_name + add_text, tickers=tickers if tickers else ticker, full_history=full_history),
                        tickers=tickers if tickers else ticker,
                        **kwargs
                    )
                except Exception as e:
                    # print(f"First attempt with tickers failed: {e}")
                    # Second attempt: Call plot_function without tickers
                    return plot_function(
                        data(dataset_name, full_history=full_history))
            else:
                # Call the plot function directly with the DataFrame
                return plot_function(df, **kwargs)
        except Exception as e:
            # print(f"Error occurred: {e}") ## These cause errors, because accounting/weekly (second part not added)
            # better to define them inside the function, or update the PLOT_FUNCTION_MAPPER (not necessary though)

            return plot_function(**kwargs)

    # If source is database, handle the database data case
    elif source == "database":
        # Retrieve datasets from the data function
        datasets = data(
            dataset_name + "/charts",
            chart=chart_type,
            tickers=tickers,
            purge_cache=purge_cache,
            **kwargs,
        )

        # Check if datasets are retrieved successfully
        if datasets is None:
            print(
                f"Failed to retrieve data for {dataset_name} with chart type {chart_type} and tickers {tickers}"
            )
            return None

        # Check if datasets is a list of datasets (one for each ticker)
        if isinstance(datasets, list):
            for dataset in datasets:
                plot_function(
                    dataset, **kwargs
                )  # Pass kwargs to the plot function for each dataset
        else:
            # Handle the single dataset case
            return plot_function(
                datasets, **kwargs
            )

    else:
        raise ValueError(f"Source {source} is not recognized.")

