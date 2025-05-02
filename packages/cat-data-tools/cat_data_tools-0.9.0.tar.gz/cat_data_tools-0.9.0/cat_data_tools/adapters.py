import pandas as pd


def Adapter_for_path_to_dataframe(path):
    file_extension = path.split(".")[-1]
    choices = {"csv": Adapter_from_csv_path(path), "": Adapatador_from_empty_path()}
    return choices[file_extension]


class Adapter_from_csv_path:
    def __init__(self, path) -> None:
        self.path = path

    def get_dataframe(self):
        return pd.read_csv(self.path)


class Adapatador_from_empty_path:
    def __init__(self):
        pass

    def get_dataframe(self):
        default_path = "cat_data_tools/default_traps_list"
        return pd.read_pickle(default_path)
