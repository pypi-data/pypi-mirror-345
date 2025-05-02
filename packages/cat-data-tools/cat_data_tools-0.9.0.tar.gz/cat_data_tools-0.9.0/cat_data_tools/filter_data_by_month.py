import pandas as pd


def summarize_effort_captures(effort_data):
    monthly_data = sum_monthly_effort_and_captures(effort_data)
    monthly_data = add_date_column(monthly_data)
    monthly_data = monthly_data.drop(columns=["month_and_year", "Zona"])
    return monthly_data


def summarize_effort_captures_and_add_trappers(monthly_trappers, effort_data):
    monthly_data = summarize_effort_captures(effort_data)
    monthly_data["Tramperos"] = monthly_trappers["Tramperos"]
    return monthly_data


def add_date_column(monthly_data):
    monthly_data.reset_index(inplace=True)
    monthly_data["Fecha"] = monthly_data.month_and_year + "-01"
    return monthly_data


def sum_monthly_effort_and_captures(effort_data: pd.DataFrame):
    effort_data["month_and_year"] = effort_data.Fecha.str[:7]
    monthly_grouped_data = effort_data.groupby(by="month_and_year")
    return monthly_grouped_data.sum(numeric_only=True)
