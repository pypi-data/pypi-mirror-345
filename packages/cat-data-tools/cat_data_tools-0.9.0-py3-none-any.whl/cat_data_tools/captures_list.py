def join_trap_info_with_captures(captures, traps_info):
    captures_df = select_captures_from_daily_status(captures)
    joined_dataframe = captures_df.join(traps_info.set_index("ID_de_trampa"), on="ID_de_trampa")
    return joined_dataframe.drop(columns=["Estado_trampa"])


def select_captures_from_daily_status(daily_status):
    return daily_status[daily_status["Estado_trampa"] == "X"]
