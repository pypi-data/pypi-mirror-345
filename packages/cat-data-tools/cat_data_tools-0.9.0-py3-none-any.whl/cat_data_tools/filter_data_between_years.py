import pandas as pd


def filter_data_between_years(monthly_data, initial_year, final_year=2260):
    data_after_year = filter_data_after_year(monthly_data, initial_year)
    return filter_data_before_year(data_after_year, final_year)


def filter_data_after_year(monthly_data, year):
    monthly_data_copy = str_2_datetime(monthly_data)
    return monthly_data_copy[monthly_data_copy.Fecha.dt.year >= year]


def filter_data_before_year(monthly_data, year):
    monthly_data_copy = str_2_datetime(monthly_data)
    return monthly_data_copy[monthly_data_copy.Fecha.dt.year <= year]


def str_2_datetime(monthly_data):
    monthly_data_copy = monthly_data.copy()
    monthly_data_copy["Fecha"] = pd.to_datetime(monthly_data_copy.Fecha, format="%Y-%m-%d")
    return monthly_data_copy
