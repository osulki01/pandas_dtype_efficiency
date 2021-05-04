"""
Evaluating pandas DataFrames to see whether the data can be compressed in a lossless manner.
"""

# Standard libraries
from typing import Dict, List, Union

# Third party libraries
import numpy as np
import pandas as pd


class DataFrameChecker:
    """
    Evaluate a pandas DataFrame to see whether its memory usage can be reduced whilst still preserving its data.
    """

    def __init__(self, df: pd.DataFrame, categorical_threshold: int = 15, float_size: int = 16):
        """
        Initialise checker with the DataFrame that needs to be evaluated.

        Parameters
        ----------
        df : pandas DataFrame
            Data to be checked to see whether any columns could reduce their memory usage.
        categorical_threshold : int (default 15)
            The maximum number of distinct values in a column of strings to suggest transforming it into a categorical
            column.
        float_size : int (default 16)
            The desired numpy float type; 16: numpy float16, 32: numpy float23, 64: numpy float64 (the pandas default).
        """

        self._all_possible_improvements = {}
        self._dataframe_has_been_analysed = False
        self._df = df
        self._categorical_threshold = categorical_threshold
        self._columns_by_type = self._separate_dtypes()

        if float_size not in [16, 32, 64]:
            raise ValueError('float_size must correspond to a numpy.float (one of 16, 32, or 64)')
        self._float_size = float_size

    def cast_dataframe_to_lower_memory_version(self) -> Union[pd.DataFrame, None]:
        """
        Take the original DataFrame and create a new one in which the appropriate columns have been cast to a
        lower-memory data type.

        Returns
        -------
        pandas DataFrame
            Original data represented in lower-memory data types where possible.
        """

        if not self._dataframe_has_been_analysed:
            raise UserWarning(
                'DataFrame has not been analysed for improvements yet. Run `identify_possible_improvements` method '
                'first.'
            )

        if not self._all_possible_improvements:
            raise UserWarning('No possible improvements have been found after analysing DataFrame.')

        lower_memory_df = self._df.astype(dtype=self._all_possible_improvements)

        original_df_memory_size_bytes = self._df.memory_usage(deep=True).sum()
        new_df_memory_size_bytes = lower_memory_df.memory_usage(deep=True).sum()

        print(f'Original DataFrame memory: {(original_df_memory_size_bytes / 1024):,.2f} megabytes')
        print(f'New DataFrame memory: {(new_df_memory_size_bytes / 1024):,.2f} megabytes')
        return lower_memory_df

    def _check_if_integer_sizes_can_be_reduced(self) -> Dict[str, type]:
        """
        Evaluate each integer column and see whether it can be reduced from int64 to a smaller integer type.

        Returns
        -------
        dict
            Mapping between column name and a reduced integer size which can accommodate its values.
        """

        # Range of values which different integer sizes can accommodate
        integer_ranges = {
            '8_min': -128, '8_max': 127,
            '16_min': -32768, '16_max': 32767,
            '32_min': -2147483648, '32_max': 2147483647
        }

        # Mapping between integer size and numpy type
        integer_size_to_numpy_type = {
            8: np.int8,
            16: np.int16,
            32: np.int32
        }

        possible_improvements = {}

        int_columns = self._columns_by_type.get('int')

        # Stop if no integer columns exist
        if not int_columns:
            return possible_improvements

        # Check if column could be accommodated within a smaller integer size
        for col in int_columns:
            min_val = self._df[col].min()
            max_val = self._df[col].max()

            for int_size in [8, 16, 32]:
                if min_val >= integer_ranges[f'{int_size}_min'] and max_val <= integer_ranges[f'{int_size}_max']:
                    possible_improvements[col] = integer_size_to_numpy_type[int_size]
                    break

        return possible_improvements

    def _check_if_strings_could_be_categorical(self) -> Dict[str, str]:
        """
        Evaluate each string column and see whether it contains a low number of distinct values, indicating it could
        be represented as a categorical variable.

        Returns
        -------
        dict
            Any columns containing strings which could be transformed into a categorical variable.
        """

        possible_improvements = {}

        string_columns = self._columns_by_type.get('object')

        # Stop if no string columns exist
        if not string_columns:
            return possible_improvements

        for col in string_columns:
            if self._df[col].nunique() <= self._categorical_threshold:
                possible_improvements[col] = 'category'

        return possible_improvements

    def _flag_float_column_improvements(self) -> Dict[str, type]:
        """
        Map each float column and how it could be represented in a lower precision.

        Returns
        -------
        dict
            Any float columns which could be reduced to the desired level of precision.
        """

        possible_improvements = {}

        # No need to map if desired float size is the pandas default (64)
        if self._float_size == 64:
            return possible_improvements

        # Mapping between desired float size and numpy type
        float_size_to_numpy_type = {
            16: np.float16,
            32: np.float32
        }

        float_columns = self._columns_by_type.get('float')

        # Stop if no float columns exist
        if not float_columns:
            return possible_improvements

        for col in float_columns:
            possible_improvements[col] = float_size_to_numpy_type[self._float_size]

        return possible_improvements

    def get_possible_dtypes(self) -> Dict[str, type]:
        """
        Retrieve a dictionary containing any columns with the potential for reduced memory, and the dtype that can be
        used to represent them in a more efficient manner.

        Returns
        -------
        dict
            Any columns with the potential for reduced memory, and the dtype that can be used to represent them in a
            more efficient manner. Dictionary is empty if no possible improvements founds.
        """

        return self._all_possible_improvements

    def identify_possible_improvements(self) -> None:
        """
        Analyse the DataFrame and store a dictionary containing any column with the potential for reduced memory, and
        the dtype that can be used to represent it in a more efficient manner.
        """

        print('Checking float columns if reduced precision requested')
        float_improvements = self._flag_float_column_improvements()
        self._all_possible_improvements.update(float_improvements)

        print('Checking integer columns to see whether a smaller size can be used')
        integer_improvements = self._check_if_integer_sizes_can_be_reduced()
        self._all_possible_improvements.update(integer_improvements)

        print('Checking string columns to see if they be assigned to repeated categories')
        categorical_improvements = self._check_if_strings_could_be_categorical()
        self._all_possible_improvements.update(categorical_improvements)

        self._dataframe_has_been_analysed = True
        print('Done')

    def _separate_dtypes(self) -> Dict[str, List[str]]:
        """
        Create a mapping between data types and the columns that belong to that data type. Only data types which have
        the potential for reduced memory usage are included.

        Returns
        -------
        dict
            Mapping between data type and the columns which correspond to that data type.
        """

        columns_by_dtype = {}

        for data_type in ['float', 'int', 'object']:
            relevant_columns = list(self._df.select_dtypes(include=data_type).columns)

            if relevant_columns:
                columns_by_dtype[data_type] = relevant_columns

        return columns_by_dtype
