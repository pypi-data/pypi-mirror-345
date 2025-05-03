"""Conftest.py is kind overkill, but allows reuse between function behaviour and checking test assertions are good."""

import polars as pl
from pytest import fixture


@fixture
def raw_struct_df() -> pl.DataFrame:
    return pl.DataFrame({"a": [-42, 13], "b": [-42, 0]})


@fixture
def raw_struct_df_singular() -> pl.DataFrame:
    return pl.DataFrame({"a": [-42, 32]})


@fixture
def int_dtype_struct() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "a": list(range(11)),
            "b": [1 for _ in range(11)],
            "c": [3 for _ in range(11)],
            "d": [1 for _ in range(11)],
            "e": [1 for _ in range(11)],
        }
    ).cast(
        {
            "a": pl.Int64,
            "b": pl.Int64,
            "c": pl.Int8,
            "d": pl.Int8,
            "e": pl.Int8,
        }
    )
    return df


@fixture
def expected_int64_neg_42():
    return pl.Series("test", [15244781726809025498], dtype=pl.UInt64)


@fixture
def expected_int32_neg_42():
    return pl.Series("test", [17010062867703544896], dtype=pl.UInt64)


@fixture
def expected_int8_42():
    return pl.Series("test", [3146795401079207122], dtype=pl.UInt64)


@fixture
def expected_uint64_42():
    return pl.Series("test", [3146795401079207122], dtype=pl.UInt64)


@fixture
def expected_uint32_42():
    return pl.Series("test", [3146795401079207122], dtype=pl.UInt64)


@fixture
def expected_int_struct():
    return pl.Series("test", [78953510757616805, 10151173556673123992], dtype=pl.UInt64)


@fixture
def expected_int_struct_singular():
    return pl.Series("test", [15244781726809025498, 4321950247308341530], dtype=pl.UInt64)


@fixture
def expected_int_dtype_struct():
    return pl.Series(
        "test",
        [
            2118545466179008139,
            10189109270930801923,
            1465386500655181257,
            392558415707402039,
            6199085648451372351,
            2821818006384607294,
            3191725983741710825,
            6499840305021931898,
            13511426428479343456,
            14251501900179806287,
            2179004388157926424,
        ],
        dtype=pl.UInt64,
    )
