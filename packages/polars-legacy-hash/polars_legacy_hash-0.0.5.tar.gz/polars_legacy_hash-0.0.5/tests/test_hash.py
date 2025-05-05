import polars as pl
from polars.testing import assert_frame_equal

import polars_legacy_hash as plh  # noqa: F401


def test_legacy_hash_int64(expected_int64_neg_42):
    df = pl.Series([-42], dtype=pl.Int64).to_frame("test")
    result = df.select(plh.legacy_hash(pl.col("test")))
    assert_frame_equal(result, expected_int64_neg_42.to_frame())


def test_legacy_hash_int32(expected_int32_neg_42):
    df = pl.Series([-42], dtype=pl.Int32).to_frame("test")
    result = df.select(plh.legacy_hash(pl.col("test")))
    assert_frame_equal(result, expected_int32_neg_42.to_frame())


def test_legacy_hash_int8(expected_int8_42):
    df = pl.Series([42], dtype=pl.Int8).to_frame("test")
    result = df.select(plh.legacy_hash(pl.col("test")))
    assert_frame_equal(result, expected_int8_42.to_frame())


def test_int_struct(raw_struct_df, expected_int_struct):
    df = raw_struct_df
    print(df.dtypes)
    result = pl.select(plh.legacy_hash(df.to_struct("test")))
    print(result)

    assert_frame_equal(result, expected_int_struct.to_frame())


def test_int_struct_singular(raw_struct_df_singular, expected_int_struct_singular):
    df = raw_struct_df_singular
    print(df.dtypes)
    result = pl.select(plh.legacy_hash(df.to_struct("test")))
    print(result)

    assert_frame_equal(result, expected_int_struct_singular.to_frame())


def test_int_dtype_struct(int_dtype_struct, expected_int_dtype_struct):
    # https://github.com/m-richards/polars_legacy_hash/issues/3

    result = pl.select(plh.legacy_hash(int_dtype_struct.to_struct("test")))
    assert_frame_equal(result, expected_int_dtype_struct.to_frame())
