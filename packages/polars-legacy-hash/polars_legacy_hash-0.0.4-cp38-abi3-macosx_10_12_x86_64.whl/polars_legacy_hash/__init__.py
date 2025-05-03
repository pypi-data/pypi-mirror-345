from __future__ import annotations

from pathlib import Path

try:
    import polars  # noqa: F401
except ImportError as e:
    raise ImportError(
        "polars-legacy-hash requires polars or polars-u64-idx to be installed. Please install either of these directly"
    ) from e

import polars as pl
from packaging.version import Version

try:
    from polars._typing import IntoExpr
except ImportError:
    from polars.type_aliases import IntoExpr  # type: ignore[no-redef] # noqa:I001

from polars_legacy_hash._internal import __version__ as __version__

if Version(pl.__version__) < Version("0.20.10"):
    raise ImportError("polars-legacy-hash requires a minimum of polars==0.20.10")

elif Version(pl.__version__) >= Version("0.20.16"):
    from polars.plugins import register_plugin_function

    def legacy_hash(expr: IntoExpr) -> pl.Expr:
        """Polars 0.20.10 hash."""
        return register_plugin_function(
            plugin_path=Path(__file__).parent,
            function_name="legacy_hash",
            args=expr,
            is_elementwise=True,
        )
else:
    from polars.type_aliases import PolarsDataType  # type:ignore[import-not-found]
    from polars.utils.udfs import _get_shared_lib_location  # type:ignore[import-not-found]

    def parse_into_expr(
        expr: IntoExpr,
        *,
        str_as_lit: bool = False,
        list_as_lit: bool = True,
        dtype: PolarsDataType | None = None,
    ) -> pl.Expr:
        """Parse a single input into an expression."""
        if isinstance(expr, pl.Expr):
            pass
        elif isinstance(expr, str) and not str_as_lit:
            expr = pl.col(expr)
        elif isinstance(expr, list) and not list_as_lit:
            expr = pl.lit(pl.Series(expr), dtype=dtype)
        else:
            expr = pl.lit(expr, dtype=dtype)
        return expr

    lib = _get_shared_lib_location(__file__)

    def legacy_hash(expr: IntoExpr) -> pl.Expr:
        """Polars 0.20.10 hash."""
        expr = parse_into_expr(expr)
        return expr.register_plugin(
            lib=lib,
            symbol="legacy_hash",
            args=[],
            is_elementwise=True,
        )


__all__ = ["legacy_hash"]
