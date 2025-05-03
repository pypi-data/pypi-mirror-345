# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "polars==1.27.1",
#     "polars_legacy_hash",
# ]
# ///


import polars as pl

import polars_legacy_hash as plh

print(f"Hashing with polars={pl.__version__} directly (not consistent!):")
s = pl.Series([42])
print(s.hash().item())
print("Using polars_legacy_hash:")
result = s.to_frame("test").select(plh.legacy_hash(pl.col("test"))).to_series()
print(result.item())
