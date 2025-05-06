# Inside plot/get_plot.py
from sovai import data

# Adjust the import to the new subpackage structure
from .reports.bankruptcy.bankruptcy_monthly_top import *
from .reports.accounting.accounting_balance_sheet import *
from .reports.general.general_plots import *
from .reports.news.news_econometric_analysis import *

# create_interactive_report

REPORT_FUNCTION_MAPPER = {
    ("bankruptcy", "ranking"): (general_ranking, "probability", "Probability"),
    ("bankruptcy", "change"): (general_ranking_change, "probability", "Probability"),
    ("corprisk/accounting", "ranking"): (
        general_ranking,
        "average",
        "Accounting Risks",
    ),
    ("corprisk/accounting", "change"): (
        general_ranking_change,
        "average",
        "Accounting Risks",
    ),
    ("corprisk/events", "ranking"): (general_ranking, "average", "Event Risks"),
    ("corprisk/events", "change"): (general_ranking_change, "average", "Event Risks"),
    ("corprisk/risks", "ranking"): (general_ranking, "risk_ind_adjs", "Total Risks"),
    ("corprisk/risks", "change"): (
        general_ranking_change,
        "risk_ind_adjs",
        "Total Risks",
    ),
    ("corprisk/misstatement", "ranking"): (
        general_ranking,
        "average",
        "Misstatement Risks",
    ),
    ("corprisk/misstatement", "change"): (
        general_ranking_change,
        "average",
        "Misstatement Risks",
    ),
    ("institutional/flow_prediction", "ranking"): (
        general_ranking,
        "flow_prediction",
        "Flow Prediction",
    ),
    ("institutional/flow_prediction", "change"): (
        general_ranking_change,
        "flow_prediction",
        "Flow Prediction",
    ),
    ("bankruptcy", "pca"): report_accounting_diff_average,
    ("accounting", "balance_sheet"): jupyter_html_assets,

    ("news", "econometric"): create_interactive_report,
    
    # Add other mappings as needed
}


def report(dataset_name, report_type="sector-top", **kwargs):
    try:
        report_function_info = REPORT_FUNCTION_MAPPER[(dataset_name, report_type)]
    except KeyError:
        raise ValueError(
            f"Displaying report for {dataset_name} with report type {report_type} not found."
        )

    if isinstance(report_function_info, tuple):
        report_function, *additional_args = report_function_info
    else:
        report_function = report_function_info
        additional_args = []

    df = kwargs.get("df")
    if df is None:
        try:
            if report_type == "ranking":
                df = data(dataset_name, frequency="latest")
            elif report_type == "change":
                print("change")
                df = data(dataset_name, frequency="difference")
            elif report_type == "previous":
                df = data(dataset_name, frequency="previous")
            else:
                df = data(dataset_name)
        except:
            try:
                df = data(dataset_name)
            except:
                return report_function(*additional_args, **kwargs)

    # Use the correct report function based on the report type
    if report_type == "change":
        return general_ranking_change(df, *additional_args, **kwargs)
    elif report_type in ["ranking", "previous"]:
        return general_ranking(df, *additional_args, **kwargs)
    else:
        return report_function(df, *additional_args, **kwargs)



# def report(dataset_name, report_type="sector-top", **kwargs):
#     # Extract the DataFrame from kwargs
#     df = kwargs.get('df')

#     # Ensure that a DataFrame is provided
#     if df is None:
#         print(f"DataFrame is required, downloading sov.data({dataset_name}) on your behalf to use as sov.report('{dataset_name}', df=dataframe)")
#         df = data(dataset_name)

#     # Find the plotting function in the mapper
#     report_function_info = REPORT_FUNCTION_MAPPER.get((dataset_name, report_type))

#     if report_function_info:
#         # Check if report_function_info is a tuple (indicating additional arguments)
#         if isinstance(report_function_info, tuple):
#             # Extract the function and its additional arguments
#             report_function, *additional_args = report_function_info
#             # Call the plotting function with the DataFrame, additional arguments, and any keyword arguments
#             return report_function(df, *additional_args, **kwargs)
#         else:
#             # If it's not a tuple, it's just the function
#             report_function = report_function_info
#             # Call the plotting function with the DataFrame and any keyword arguments
#             return report_function(df, **kwargs)
#     else:
#         raise ValueError(f"Displaying report for {dataset_name} with report type {report_type} not found.")
