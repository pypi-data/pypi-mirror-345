from datetime import datetime, timedelta
import pandas as pd
from IPython.display import display, HTML
from sovai import data
from sovai.api_config import ApiConfig
import requests


import requests
from sovai.api_config import ApiConfig

def generate_analyst_commentary(html_output, verbose=True):
    url = f"{ApiConfig.base_url}/llm/generate_commentary_second"
    headers = {
        "Authorization": f"Bearer {ApiConfig.token}",
        "Content-Type": "application/json"
    }
    payload = {"html_output": html_output}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        commentary = result.get("commentary")
        
        # if verbose:
        #     print(f"Generated commentary: {commentary[:100]}...")  # Print first 100 characters
        
        return commentary
    except requests.RequestException as e:
        if verbose:
            print(f"Request failed LLM commentary: {e}")
        return None


def analyze_balance_sheet_changes(ticker="MSFT"):
    today = pd.to_datetime(datetime.now().date())
    df_accounting = data("accounting/weekly", tickers=ticker)
    df_ratios = data("ratios/normal", tickers=ticker)

    df_accounting["other_current_assets"] = (
        df_accounting["current_assets"]
        - df_accounting["cash_equiv_usd"]
        - df_accounting["accounts_receivable"]
        - df_accounting["inventory_amount"]
        - df_accounting["tax_assets"]
        - df_accounting["current_investments"]
    ).clip(lower=0)
    df_accounting["other_non_current_assets"] = (
        df_accounting["non_current_assets"]
        - df_accounting["property_plant_equipment_net"]
        - df_accounting["non_current_investments"]
        - df_accounting["intangible_assets"]
    ).clip(lower=0)
    df_accounting["other_non_current_liabilities"] = (
        df_accounting["non_current_liabilities"] - df_accounting["non_current_debt"]
    ).clip(lower=0)
    df_accounting["other_current_liabilities"] = (
        df_accounting["current_liabilities"]
        - df_accounting["current_debt"]
        - df_accounting["deferred_revenue"]
        - df_accounting["tax_liabilities"]
        - df_accounting["accounts_payable"]
        - df_accounting["bank_deposits"]
    ).clip(lower=0)

    last_quarter_data = df_accounting.loc[ticker].sort_index().iloc[-1]
    last_year_data = df_accounting.loc[ticker].sort_index().iloc[-53]
    two_years_ago_data = df_accounting.loc[ticker].sort_index().iloc[-105]

    last_quarter_ratios = df_ratios.loc[ticker].sort_index().iloc[-1]
    last_year_ratios = df_ratios.loc[ticker].sort_index().iloc[-53]

    items_to_analyze = [
        ("Total Assets", "total_assets"),
        ("Current Assets", "current_assets"),
        ("Cash and Equivalents", "cash_equiv_usd"),
        ("Accounts Receivable", "accounts_receivable"),
        ("Inventory", "inventory_amount"),
        ("Non-Current Assets", "non_current_assets"),
        ("Property, Plant & Equipment", "property_plant_equipment_net"),
        ("Non-Current Investments", "non_current_investments"),
        ("Intangible Assets", "intangible_assets"),
        ("Other Non-Current Assets", "other_non_current_assets"),
        ("Total Equity", "equity_usd"),
        ("Non-Current Liabilities", "non_current_liabilities"),
        ("Non-Current Portion of Total Debt", "non_current_debt"),
        ("Other Non-Current Liabilities", "other_non_current_liabilities"),
        ("Current Liabilities", "current_liabilities"),
        ("Current Debt", "current_debt"),
        ("Deferred Revenue", "deferred_revenue"),
        ("Tax Liabilities", "tax_liabilities"),
        ("Accounts Payable", "accounts_payable"),
    ]

    analysis = f"<h1 class='dark-mode'>Balance Sheet Analysis for {ticker}</h1>"
    analysis += (
        f"<p class='dark-mode'><em>Report Date: {today.strftime('%Y-%m-%d')}</em></p>"
    )

    analysis += "<table class='dark-mode balance-sheet'>"
    analysis += "<tr><th>Item</th><th>Current Value</th><th>Previous Value</th><th>Year-over-Year Change</th></tr>"

    for item, column in items_to_analyze:
        last_quarter_value = last_quarter_data[column]
        last_year_value = last_year_data[column]
        change = last_quarter_value - last_year_value
        percent_change = (change / last_year_value) * 100

        if (pd.isna(last_quarter_value) or last_quarter_value == 0) and (
            pd.isna(last_year_value) or last_year_value == 0
        ):
            continue

        arrow = "▲" if change > 0 else "▼"
        color = "green" if change > 0 else "red"

        analysis += f"<tr><td>{item}</td><td>${last_quarter_value:,.0f}M</td><td>${last_year_value:,.0f}M</td><td><span style='color:{color}'>{arrow} {percent_change:.2f}%</span></td></tr>"

    analysis += "</table>"

    # Advanced calculations
    current_ratio = last_quarter_ratios["current_ratio"]
    quick_ratio = last_quarter_ratios["quick_ratio"]
    debt_to_equity = last_quarter_ratios["debt_equity_ratio"]
    revenue_growth = (
        (last_quarter_data["total_revenue"] - last_year_data["total_revenue"])
        / last_year_data["total_revenue"]
        * 100
    )
    revenue_growth_2y = (
        (last_year_data["total_revenue"] - two_years_ago_data["total_revenue"])
        / two_years_ago_data["total_revenue"]
        * 100
    )
    working_capital = (
        last_quarter_data["current_assets"] - last_quarter_data["current_liabilities"]
    )
    asset_turnover = last_quarter_ratios["asset_turnover"]
    return_on_equity = last_quarter_ratios["return_on_equity"]
    return_on_assets = last_quarter_ratios["return_on_assets"]

    # Additional financial metrics
    gross_profit_margin = last_quarter_ratios["gross_profit_margin"]
    operating_profit_margin = last_quarter_ratios["operating_profit_margin"]
    net_profit_margin = last_quarter_ratios["net_profit_margin"]
    earnings_per_share = last_quarter_ratios["earnings_per_share"]
    price_to_earnings = last_quarter_ratios["price_to_earnings"]

    analysis += "<div class='financial-metrics dark-mode'>"
    analysis += "<h2 class='metrics-heading'>Key Financial Metrics</h2>"
    analysis += "<div class='metrics-tables'>"
    analysis += "<table>"
    analysis += "<tr><th></th><th>Current</th><th>Previous Year</th></tr>"
    analysis += f"<tr><td>Current Ratio</td><td>{current_ratio:.2f}</td><td>{last_year_ratios['current_ratio']:.2f}</td></tr>"
    analysis += f"<tr><td>Quick Ratio</td><td>{quick_ratio:.2f}</td><td>{last_year_ratios['quick_ratio']:.2f}</td></tr>"
    analysis += f"<tr><td>Debt-to-Equity Ratio</td><td>{debt_to_equity:.2f}</td><td>{last_year_ratios['debt_equity_ratio']:.2f}</td></tr>"
    analysis += f"<tr><td>Revenue Growth (Year-over-Year)</td><td>{revenue_growth:.2f}%</td><td>{revenue_growth_2y:.2f}%</td></tr>"
    analysis += f"<tr><td>Gross Profit Margin</td><td>{gross_profit_margin:.2f}%</td><td>{last_year_ratios['gross_profit_margin']:.2f}%</td></tr>"
    analysis += f"<tr><td>Operating Profit Margin</td><td>{operating_profit_margin:.2f}%</td><td>{last_year_ratios['operating_profit_margin']:.2f}%</td></tr>"
    analysis += "</table>"
    analysis += "<table>"
    analysis += "<tr><th></th><th>Current</th><th>Previous Year</th></tr>"
    analysis += f"<tr><td>Net Profit Margin</td><td>{net_profit_margin:.2f}%</td><td>{last_year_ratios['net_profit_margin']:.2f}%</td></tr>"
    analysis += f"<tr><td>Earnings Per Share</td><td>${earnings_per_share:.2f}</td><td>${last_year_ratios['earnings_per_share']:.2f}</td></tr>"
    analysis += f"<tr><td>Price-to-Earnings Ratio</td><td>{price_to_earnings:.2f}</td><td>{last_year_ratios['price_to_earnings']:.2f}</td></tr>"
    analysis += f"<tr><td>Working Capital</td><td>${working_capital:,.0f}M</td><td>${(last_year_data['current_assets'] - last_year_data['current_liabilities']):,.0f}M</td></tr>"
    analysis += f"<tr><td>Asset Turnover Ratio</td><td>{asset_turnover:.2f}</td><td>{last_year_ratios['asset_turnover']:.2f}</td></tr>"
    analysis += f"<tr><td>Return on Equity (ROE)</td><td>{return_on_equity:.2f}%</td><td>{last_year_ratios['return_on_equity']:.2f}%</td></tr>"
    analysis += "</table>"
    analysis += "</div>"
    analysis += "</div>"

    # analysis += "<div class='analyst-commentary dark-mode'>"
    # analysis += "<h2>Analyst Commentary</h2>"

    # if current_ratio > 1.5 and quick_ratio > 1:
    #     analysis += "<p>The company demonstrates strong liquidity, with a current ratio and quick ratio above the generally accepted thresholds. This indicates a healthy ability to meet short-term obligations.</p>"
    # else:
    #     analysis += "<p>The company's liquidity position warrants attention, as the current ratio and quick ratio fall below the generally accepted thresholds. Management should focus on improving short-term liquidity to ensure the company can meet its immediate obligations.</p>"

    # if debt_to_equity < 1:
    #     analysis += "<p>The company maintains a conservative capital structure, with a debt-to-equity ratio below 1. This suggests a lower financial risk profile and provides flexibility for future growth and investments.</p>"
    # else:
    #     analysis += "<p>The company's debt-to-equity ratio exceeds 1, indicating a more aggressive capital structure. While leverage can amplify returns, it also increases financial risk. Management should closely monitor debt levels and consider deleveraging strategies if necessary.</p>"

    # if revenue_growth > 10:
    #     analysis += "<p>The company achieved impressive year-over-year revenue growth, surpassing 10%. This strong performance demonstrates the effectiveness of the company's sales strategies and market positioning. Management should capitalize on this momentum and explore further growth opportunities.</p>"
    # elif revenue_growth > 0:
    #     analysis += "<p>The company experienced positive year-over-year revenue growth, albeit at a more moderate pace. While encouraging, management should identify areas for improvement and implement strategies to accelerate growth in the coming years.</p>"
    # else:
    #     analysis += "<p>The company faced challenges in generating year-over-year revenue growth, as evidenced by the decline compared to the previous year. Management must critically assess the factors contributing to this performance and take corrective actions to restore growth trajectory.</p>"

    # if return_on_equity > 15 and return_on_assets > 5:
    #     analysis += "<p>The company delivered strong profitability, with ROE exceeding 15% and ROA surpassing 5%. These metrics highlight the efficiency in generating returns for shareholders and effectively utilizing assets. Management should strive to maintain and further improve these ratios.</p>"
    # else:
    #     analysis += "<p>The company's profitability metrics, ROE and ROA, leave room for improvement. Management should focus on enhancing operational efficiency, optimizing asset utilization, and implementing cost-saving measures to boost overall profitability.</p>"

    # analysis += "</div>"

    # Generate analyst commentary using GPT-4
    # print(analysis)

    
    analyst_commentary = generate_analyst_commentary(analysis)

    # print(analyst_commentary)

    analysis += "<div class='analyst-commentary dark-mode'>"
    analysis += "<h2>Analyst Commentary</h2>"
    analysis += analyst_commentary
    analysis += "</div>"

    return analysis


custom_css = """
<style>
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        padding: 20px;
        color: #fff;
        background-color: #000;
    }
    .dark-mode {
        color: #fff;
        background-color: #000;
    }
    h1.dark-mode {
        color: #4fc3f7;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    h2 {
        color: #4fc3f7;
        font-size: 22px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 1px solid #616161;
    }
    p.dark-mode {
        font-size: 16px;
        margin-bottom: 10px;
    }
    table.dark-mode {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    th, td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid #616161;
    }
    th {
        background-color: #212121;
        font-weight: bold;
    }
    .balance-sheet {
        border: 1px solid #616161;
        border-radius: 5px;
    }
    .financial-metrics {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 30px;
        border: 1px solid #616161;
        border-radius: 5px;
        padding: 20px;
    }
    .metrics-heading {
        text-align: center;
        margin-bottom: 20px;
    }
    .metrics-tables {
        display: flex;
        justify-content: space-between;
        width: 100%;
    }
    .metrics-tables table {
        width: 48%;
    }
    .analyst-commentary.dark-mode {
        background-color: #212121;
        padding: 20px;
        border-radius: 5px;
        margin-top: 30px;
        border: 1px solid #616161;
    }
    .analyst-commentary.dark-mode p {
        margin-bottom: 15px;
    }
</style>
"""



def jupyter_html_assets(ticker="AAPL"):
    analysis = analyze_balance_sheet_changes(ticker=ticker)
    return display(HTML(custom_css + analysis))
