# Third party libraries
import numpy as np
import pandas as pd
import pytest

# Internal imports
import pandas_dtype_efficiency as pd_eff


# Mock data for consistent evaluation
MOCK_DF = pd.DataFrame(
    data={
        'floats': [-0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0.5],
        'int_smaller_than_int8': [-128, 0, 0, 0, 0, 0, 0, 0, 0, 127],
        'int_smaller_than_int16': [-32768, 0, 0, 0, 0, 0, 0, 0, 0, 32767],
        'int_smaller_than_int32': [-2147483648, 0, 0, 0, 0, 0, 0, 0, 0, 2147483647],
        'int_smaller_than_int64': [-9223372036854775808, 0, 0, 0, 0, 0, 0, 0, 0, 9223372036854775807],
        'category_strings': ['C1', 'C2', 'C1', 'C2', 'C1', 'C2', 'C1', 'C2', 'C1', 'C2'],
        'varied_strings': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
        'ineligible_column': [True, False, True, False, True, False, True, False, True, False]
    }
)


# Mock data where no improvements can be made
MOCK_DF_NO_IMPROVEMENTS = pd.DataFrame(data={'bool_1': [True, False], 'bool_2': [True, False]})


@pytest.fixture
def checker() -> pd_eff.DataFrameChecker:
    """
    Establish a consistent checker with the same mock data.
    """

    return pd_eff.DataFrameChecker(df=MOCK_DF)


class TestDataFrameChecker:
    """
    Tests for DataFrameChecker.
    """

    def test_cast_dataframe_to_lower_memory_version(self, checker):
        """
        DataFrame has the appropriate columns converted to new data types.
        """

        expected_output = pd.Series(
            data={
                'floats': np.dtype('float16'),
                'int_smaller_than_int8': np.dtype('int8'),
                'int_smaller_than_int16': np.dtype('int16'),
                'int_smaller_than_int32': np.dtype('int32'),
                'int_smaller_than_int64': np.dtype('int64'),
                'category_strings': 'category',
                'varied_strings': 'category',
                'ineligible_column': np.dtype('bool')
            }
        )

        checker.identify_possible_improvements()
        lower_memory_df = checker.cast_dataframe_to_lower_memory_version()
        lower_memory_df_dtypes = lower_memory_df.dtypes

        pd.testing.assert_series_equal(left=lower_memory_df_dtypes, right=expected_output)

    def test_cast_dataframe_to_lower_memory_version_should_be_analysed_first(self, checker):
        """
        Warning is given if user tries to cast the DataFrame without having first evaluated it.
        """

        with pytest.raises(
                expected_exception=UserWarning,
                match='DataFrame has not been analysed for improvements yet. Run `identify_possible_improvements` '
                      'method first.*'
        ):
            checker.cast_dataframe_to_lower_memory_version()

    def test_cast_dataframe_to_lower_memory_version_warns_if_no_improvements(self):
        """
        Warning is given if DataFrame has no possible improvements.
        """

        checker = pd_eff.DataFrameChecker(df=MOCK_DF_NO_IMPROVEMENTS)
        checker.identify_possible_improvements()

        with pytest.raises(
                expected_exception=UserWarning,
                match='No possible improvements have been found after analysing DataFrame.*'
        ):
            checker.cast_dataframe_to_lower_memory_version()

    def test__check_if_integer_sizes_can_be_reduced(self, checker):
        """
        Possible improvements to the integer size of each column are correctly found.
        """

        expected_output = {
            'int_smaller_than_int8': np.int8,
            'int_smaller_than_int16': np.int16,
            'int_smaller_than_int32': np.int32
        }

        assert checker._check_if_integer_sizes_can_be_reduced() == expected_output

    @pytest.mark.parametrize(
        argnames='categorical_threshold, expected_output',
        argvalues=[
            (5, {'category_strings': 'category'}),
            (15, {'category_strings': 'category', 'varied_strings': 'category'})
        ]
    )
    def test__check_if_strings_could_be_categorical(self, categorical_threshold, expected_output):
        """
        Possible categorical representations of string columns are found.
        """

        # Overwrite default
        checker = pd_eff.DataFrameChecker(df=MOCK_DF, categorical_threshold=categorical_threshold)

        assert checker._check_if_strings_could_be_categorical() == expected_output

    @pytest.mark.parametrize(
        argnames=('float_size', 'expected_output'),
        argvalues=[(16, {'floats': np.float16}), (32, {'floats': np.float32}), (64, {})]
    )
    def test__flag_float_column_improvements(self, float_size, expected_output):
        """
        Possible float columns are marked for a lower precision representation, or ignored if the default pandas value
        of 64 is requested.
        """

        # Overwrite default
        checker = pd_eff.DataFrameChecker(df=MOCK_DF, float_size=float_size)

        assert checker._flag_float_column_improvements() == expected_output

    def test_get_potential_dtypes(self, checker):
        """
        All possible improvements are compiled into a single dictionary.
        """

        checker.identify_possible_improvements()

        expected_output = {
            'floats': np.float16,
            'int_smaller_than_int8': np.int8,
            'int_smaller_than_int16': np.int16,
            'int_smaller_than_int32': np.int32,
            'category_strings': 'category',
            'varied_strings': 'category'
        }

        assert checker.get_possible_dtypes() == expected_output

    def test__init_expects_valid_float_size(self):
        """
        The checker will not be created if an invalid float size is provided.
        """

        with pytest.raises(
                expected_exception=ValueError,
                match='float_size must correspond to a numpy.float (one of 16, 32, or 64)*'
        ):
            checker = pd_eff.DataFrameChecker(df=MOCK_DF, float_size=99)

    def test__separate_dtypes(self, checker):
        """
        Columns are correctly recorded in terms of how they should be checked when seeing whether their memory usage
        could be reduced.
        """

        checker._separate_dtypes()

        expected_output = {
            'float': ['floats'],
            'int': [
                'int_smaller_than_int8', 'int_smaller_than_int16', 'int_smaller_than_int32', 'int_smaller_than_int64'
            ],
            'object': ['category_strings', 'varied_strings']
        }

        assert checker._separate_dtypes() == expected_output
