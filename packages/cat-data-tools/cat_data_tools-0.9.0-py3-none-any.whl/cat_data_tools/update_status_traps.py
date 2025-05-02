def _update_status_traps(traps_info_df):
    is_id_duplicated = traps_info_df.duplicated(subset=["Tipo", "ID", "Orden"], keep=False)
    is_same_date = traps_info_df["Fecha"].duplicated(keep=False)
    should_keep = [
        not (duplicated_id and duplicated_date)
        for duplicated_id, duplicated_date in zip(is_id_duplicated, is_same_date)
    ]
    return traps_info_df[should_keep].reset_index(drop=True)
