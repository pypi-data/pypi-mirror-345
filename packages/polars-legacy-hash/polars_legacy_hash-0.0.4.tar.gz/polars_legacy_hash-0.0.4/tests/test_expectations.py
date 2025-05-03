import polars as pl
import pytest
from polars.testing import assert_series_equal

SOURCE_POLARS_VERSION = pl.__version__ == "0.20.10"
if not SOURCE_POLARS_VERSION:
    pytest.skip("module only run to confirm test assertions are good", allow_module_level=True)
old_polars_only = pytest.mark.skipif(not SOURCE_POLARS_VERSION, reason="Checking old polars behaviour")


def test_old_polars_hash(expected_int64_neg_42, expected_int32_neg_42, expected_uint64_42, expected_uint32_42):
    actual = pl.Series("test", [-42], dtype=pl.Int64).hash()
    assert_series_equal(expected_int64_neg_42, actual)
    actual = pl.Series("test", [-42], dtype=pl.Int32).hash()
    assert_series_equal(expected_int32_neg_42, actual)
    actual = pl.Series("test", [42], dtype=pl.UInt64).hash()
    assert_series_equal(expected_uint64_42, actual)
    actual = pl.Series("test", [42], dtype=pl.UInt32).hash()
    assert_series_equal(expected_uint32_42, actual)


def test_int8(expected_int8_42):
    actual = pl.Series("test", [42], dtype=pl.Int8).hash()
    assert_series_equal(expected_int8_42, actual)


def test_int_struct(raw_struct_df, expected_int_struct):
    actual = raw_struct_df.to_struct("test").hash()
    assert_series_equal(expected_int_struct, actual)


def test_int_struct2(raw_struct_df, expected_int_struct):
    actual = raw_struct_df.hash_rows().rename("test")
    assert_series_equal(expected_int_struct, actual)


def test_int_struct_singular(raw_struct_df_singular, expected_int_struct_singular):
    actual = raw_struct_df_singular.to_struct("test").hash()
    assert_series_equal(expected_int_struct_singular, actual)


def test_int_dtype_struct(int_dtype_struct, expected_int_dtype_struct):
    actual = int_dtype_struct.to_struct("test").hash()
    assert_series_equal(expected_int_dtype_struct, actual)
