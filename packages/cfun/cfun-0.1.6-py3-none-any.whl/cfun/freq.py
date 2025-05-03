import pandas as pd

import importlib.resources as pkg_resources
from . import data  # 确保 src/cfun/data/__init__.py 存在


def load_parquet(filename: str) -> pd.DataFrame:
    path = pkg_resources.files(data).joinpath(filename)
    with path.open("rb") as f:
        return pd.read_parquet(f)


FREQUENCY = load_parquet("frequency.parquet")

__all__ = [
    "FREQUENCY",
]
