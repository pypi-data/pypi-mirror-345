import pandas as pd

pd.options.display.width = None


class DataframeCleaner:
    def __init__(self, frame: pd.DataFrame):
        self.df = frame.copy()
        self._strip_values()
        self._remove_nans()

    def _strip_values(self):
        """
        This function takes class instance which is pandas dataframe and strips all values in it
        """
        self.df = self.df.map(lambda x: x.strip() if isinstance(x, str) else x)

    def _remove_nans(self):
        self.df = self.df.dropna(how='all', axis=1)
        self.df = self.df.dropna(how='all', axis=0).reset_index(drop=True)

    def adj_by_row_index(self, value: str):
        row_idx = self.df.index[self.df.eq(value).any(axis=1)]
        self.df.columns = self.df.loc[row_idx[0]].values
        self.df = self.df.drop(index=range(row_idx[0] + 1))

        return self.df

    def remove_duplicated_cols(self):
        self.df = self.df.loc[:, ~self.df.columns.duplicated()]
        return self.df

    def __repr__(self):
        return self.df.__repr__()


if __name__ == '__main__':
    # Example usage:
    df = pd.read_excel(r'C:\Users\slalnazarov\Documents\04082023.xlsx')
    cleaner = DataframeCleaner(df)
    cleaner.adj_by_row_index("Name")
    cleaner.remove_duplicated_cols()
    cleaner.df.to_clipboard()
