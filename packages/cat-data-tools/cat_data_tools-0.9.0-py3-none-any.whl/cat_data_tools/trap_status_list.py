def join_trap_ids_and_daily_status(trap_daily_status, trap_ids):
    trap_daily_status_without_na = trap_daily_status.dropna(axis=0, subset=["Estado_trampa"])
    joined_dataframe = trap_daily_status_without_na.join(
        trap_ids.set_index("ID"), on="ID_de_trampa"
    )
    return joined_dataframe
