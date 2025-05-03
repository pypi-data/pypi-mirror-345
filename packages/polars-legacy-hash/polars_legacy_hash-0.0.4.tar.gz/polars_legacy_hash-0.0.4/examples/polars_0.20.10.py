# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "polars==0.20.10",
#     "polars_legacy_hash",
# ]
# ///
import polars as pl

import polars_legacy_hash as plh

print(f"Hashing with polars={pl.__version__} directly:")
s = pl.Series(range)
print(s.hash().item())
print("Using polars_legacy_hash:")
result = s.to_frame("test").select(plh.legacy_hash(pl.col("test"))).to_series()
print(result.item())
