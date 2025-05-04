import win32com.client as client
import pandas as pd
from pywintypes import com_error
import time
from pathlib import Path

from win32com.client import makepy

makepy.GenerateFromTypeLibSpec('Excel.Application')
from evergreenlib.clean.cleaner import DataframeCleaner


class ExcelParser:
    """
    This class should be reading data from .xlsx files
    """

    def __init__(self, filepath: str, sheet_name: str, index_value: str):
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.index_value = index_value

    def read_data(self):
        try:
            xlapp = client.GetActiveObject("Excel.Application")
            print(f"Connected to existing Excel instance. Reading {Path(self.filepath).name}")
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            cleaner = DataframeCleaner(df)
            cleaner.adj_by_row_index(self.index_value)
            cleaner.remove_duplicated_cols()
            wkb.Close(SaveChanges=False)
        except com_error as e:
            print(f"COM Error: {e}")
            print(f"No active Excel instance found. Creating a new one. Reading {Path(self.filepath).name}")
            xlapp_new = client.Dispatch('Excel.Application')
            xlapp_new.Visible = True
            wkb = xlapp_new.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            cleaner = DataframeCleaner(df)
            cleaner.adj_by_row_index(self.index_value)
            cleaner.remove_duplicated_cols()
            wkb.Close(SaveChanges=False)
        return cleaner.df


class ExcelParser_retain_duplicates:
    """
    This class should be reading data from .xlsx files
    """

    def __init__(self, filepath: str, sheet_name: str, index_value: str):
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.index_value = index_value

    def read_data(self):
        try:
            xlapp = client.GetActiveObject("Excel.Application")
            print("Connected to existing Excel instance.")
            wkb = xlapp.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            cleaner = DataframeCleaner(df)
            cleaner.adj_by_row_index(self.index_value)
            # cleaner.remove_duplicated_cols()
            wkb.Close(SaveChanges=False)
        except com_error as e:
            print(f"COM Error: {e}")
            print("No active Excel instance found. Creating a new one.")
            xlapp_new = client.Dispatch('Excel.Application')
            xlapp_new.Visible = True
            wkb = xlapp_new.Workbooks.Open(self.filepath, ReadOnly=True, UpdateLinks=False)
            sht = wkb.Sheets[self.sheet_name]
            used_rng = sht.UsedRange.Value
            df = pd.DataFrame(used_rng)
            cleaner = DataframeCleaner(df)
            cleaner.adj_by_row_index(self.index_value)
            # cleaner.remove_duplicated_cols()
            wkb.Close(SaveChanges=False)
        return cleaner.df


if __name__ == "__main__":
    x = ExcelParser(
        r"V:\Findep\Incoming\test\DevOps\ARAP Project\Project\Accounting Input Data\YTD07_2023\Оборотно-сальдовая ведомость за January 2023 - July 2023 ООО  ХЕНДЭ МОБИЛИТИ ЛАБ.xls",
        'TDSheet',
        'Счет')
    print(x.read_data())
