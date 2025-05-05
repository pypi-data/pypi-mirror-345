from abc import abstractmethod, ABC
import numpy as np
from cp2025.utility.utility import fill_left_columns_ids
import pandas as pd

class Depersonalizator(ABC):
    def __init__(self, output_defaults):
        self.output_defaults = output_defaults
        self.identifiers_ids = None
        self.quasi_identifiers_ids = None
        self.sensitives_ids = None

    def depersonalize(self, df, identifiers_ids = None, quasi_identifiers_ids = 'left', sensitives_ids = None):
        if len(df) == 0:
            if self.output_defaults is not None:
                return df, *self.output_defaults
            else:
                return df

        df_is_list = type(df) == list
        df_is_pd = type(df) == pd.DataFrame
        df_columns = None
        if df_is_pd:
            df_columns = df.columns.to_list()
            df = df.to_numpy()
        df = np.array(df, dtype=object)

        if identifiers_ids is None:
            identifiers_ids = []
        if quasi_identifiers_ids is None:
            quasi_identifiers_ids = []
        if sensitives_ids is None:
            sensitives_ids = []

        if [identifiers_ids, quasi_identifiers_ids, sensitives_ids].count('left') > 1:
            raise ValueError("There can be only one ids with value 'left'")
        if identifiers_ids == 'left':
            identifiers_ids = fill_left_columns_ids(len(df[0]), quasi_identifiers_ids, sensitives_ids)
        if quasi_identifiers_ids == 'left':
            quasi_identifiers_ids = fill_left_columns_ids(len(df[0]), identifiers_ids, sensitives_ids)
        if sensitives_ids == 'left':
            sensitives_ids = fill_left_columns_ids(len(df[0]), identifiers_ids, quasi_identifiers_ids)

        self.identifiers_ids = identifiers_ids
        self.quasi_identifiers_ids = quasi_identifiers_ids
        self.sensitives_ids = sensitives_ids

        identifiers = df[:, identifiers_ids]
        quasi_identifiers = df[:, quasi_identifiers_ids]
        sensitives = df[:, sensitives_ids]

        out_identifiers, out_quasi_identifiers, *other_output = self.__depersonalize__(identifiers, quasi_identifiers, sensitives)

        if out_identifiers is None:
            out_identifiers = df[:, []]
        if out_quasi_identifiers is None:
            out_quasi_identifiers = df[:, []]

        if len(out_identifiers[0]) == 0 and len(out_quasi_identifiers[0]) == 0 and len(sensitives[0]) == 0:
            return None, *other_output

        cols = []
        cur_identifier = 0
        cur_quasi_identifier = 0
        cur_sensitive = 0
        for i in range(len(df[0])):
            if i in identifiers_ids:
                if len(out_identifiers[0]) == len(identifiers_ids):
                    cols.append(out_identifiers[:, cur_identifier])
                    cur_identifier += 1
            if i in quasi_identifiers_ids:
                if len(out_quasi_identifiers[0]) == len(quasi_identifiers_ids):
                    cols.append(out_quasi_identifiers[:, cur_quasi_identifier])
                    cur_quasi_identifier += 1
            if i in sensitives_ids:
                cols.append(sensitives[:, cur_sensitive])
                cur_sensitive += 1
        output_df = np.column_stack(cols)

        if df_is_list:
            return output_df.tolist() if out_quasi_identifiers is not None else None, *other_output

        if df_is_pd:
            return pd.DataFrame(data=output_df, columns=df_columns, dtype=object) if out_quasi_identifiers is not None else None, *other_output

        return output_df, *other_output

    @abstractmethod
    def __depersonalize__(self, identifiers, quasi_identifiers, sensitives):
        pass
