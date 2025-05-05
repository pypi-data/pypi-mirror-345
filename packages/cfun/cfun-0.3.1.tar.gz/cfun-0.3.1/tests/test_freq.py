from cfun.freq import FREQUENCY
from cfundata import ALL_FREQUENCY_PARQUENT_PATH
import pandas as pd


def test_all_frequency():
    df = pd.read_parquet(ALL_FREQUENCY_PARQUENT_PATH)
    print(df.head())
    print(ALL_FREQUENCY_PARQUENT_PATH)


def test_frequency():
    print(FREQUENCY.head())
    print(FREQUENCY.columns)
    print(len(FREQUENCY))
    assert len(FREQUENCY) > 0, "FREQUENCY 数据为空"
    assert "word" in FREQUENCY.columns, "FREQUENCY 缺少 'word' 列"
    assert "count" in FREQUENCY.columns, "FREQUENCY 缺少 'count' 列"
