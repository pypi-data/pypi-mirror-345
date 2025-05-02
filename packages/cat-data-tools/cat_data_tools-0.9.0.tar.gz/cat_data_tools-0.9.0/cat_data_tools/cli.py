from cat_data_tools.filter_data_by_month import (
    summarize_effort_captures_and_add_trappers,
    summarize_effort_captures,
)
from cat_data_tools.filter_data_between_years import filter_data_between_years
from cat_data_tools.update_status_traps import _update_status_traps
import cat_data_tools as cdt
import pandas as pd
import typer


app = typer.Typer()


@app.command()
def join_traps_ids_and_daily_status(
    trap_daily_status_path: str = "", traps_ids_path: str = "", output_path: str = ""
):
    trap_daily_status = pd.read_csv(trap_daily_status_path)
    traps_ids = pd.read_csv(traps_ids_path)
    joined_df = cdt.join_trap_ids_and_daily_status(trap_daily_status, traps_ids)
    joined_df.to_csv(output_path, index=False)


@app.command()
def join_captures_with_traps_info(
    trap_daily_status_path: str = "", traps_info_path: str = "", output_path: str = ""
):
    daily_status_df = cdt.Adapter_for_path_to_dataframe(trap_daily_status_path).get_dataframe()
    traps_info_df = cdt.Adapter_for_path_to_dataframe(traps_info_path).get_dataframe()
    joined_df = cdt.join_trap_info_with_captures(daily_status_df, traps_info_df)
    joined_df.to_csv(output_path, index=False)


@app.command(help="Write monthly summary from weekly summary without trappers")
def write_monthly_summary_without_trappers(weekly_data_path: str = "", output_path: str = ""):
    effort_data = pd.read_csv(weekly_data_path)
    monthly_data = summarize_effort_captures(effort_data)
    monthly_data.to_csv(output_path, index=False)


@app.command(help="Write monthly summary from weekly summary")
def write_monthly_summary(
    weekly_data_path: str = "", monthly_trappers_path: str = "", output_path: str = ""
):
    effort_data = pd.read_csv(weekly_data_path)
    monthly_trappers = pd.read_csv(monthly_trappers_path)
    monthly_data = summarize_effort_captures_and_add_trappers(monthly_trappers, effort_data)
    monthly_data.to_csv(output_path, index=False, na_rep="NA")


@app.command(help="Filter monthly summary between years")
def filter_monthly_summary(
    monthly_data_path: str = "",
    output_path: str = "",
    initial_year: int = 2014,
    final_year: int = 2019,
):
    dataframe = pd.read_csv(monthly_data_path)
    filtered_dataframe = filter_data_between_years(dataframe, initial_year, final_year)
    filtered_dataframe.to_csv(output_path, index=False, na_rep="NA")


@app.command()
def update_status_traps(data_path: str = typer.Option(), output_path: str = typer.Option()):
    traps_info_df = pd.read_csv(data_path)
    updated_traps_info = _update_status_traps(traps_info_df)
    updated_traps_info.to_csv(output_path, index=False, na_rep="NA")


@app.command()
def version():
    print(cdt.__version__)
