import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

## 对于3.12的版本， 可以使用快捷的批处理函数：
# from itertools import batched


######################################################
########## 公共部分 ##################
###########################################
## 这里定义一个 batched函数， 用于将一个迭代器分成多个批次， python3.12版本可以直接使用: from itertools import batched
def batched(iterable, n):
    """Returns a batch of n items at a time."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch


def parallel_handle(Iterative, func, args=(), max_workers=6):
    """
    并行处理函数--一个简单的模板
    :param Iterative: 迭代器
    :param func: 处理函数
    :param args: 处理函数的参数, 如果是多个参数, 这些参数应该是固定值
    :param max_workers: 最大工作线程数
    :return: 处理结果
    :note: 该函数会将Iterative中的每个元素传入func中进行处理， 并返回处理结果
    """

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, f, *args) for f in Iterative]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                assert False, f"处理失败， 错误信息: {e}"
    return results


######################################################
########## csv ##################
###########################################


def load_csv(file, encoding="utf-8"):
    """
    读取csv文件
    :param file: 文件路径
    :param encoding: 编码格式
    :return: DataFrame
    """
    return pd.read_csv(file, encoding=encoding)


def parallel_load_csv(files, encoding, max_workers=6, batch_size=6):
    """
    并行处理csv文件
    :param files: 文件列表
    :param max_workers: 最大工作线程数
    :param batch_size: 每批处理的文件数， 当设置很大的时候，即全部文件一起处理时，（前提每个文件都很小），
    """
    all_dfs = []
    batched_files = batched(files, batch_size)
    for idx, batch in enumerate(batched_files):
        dfs = parallel_handle(batch, load_csv, args=(encoding,), max_workers=max_workers)
        if dfs:
            all_dfs.append(pd.concat(dfs, ignore_index=True))
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()


######################################################
########## txt ##################
###########################################
def load_txt(file_path: str, encoding="utf-8") -> str:
    """加载文本文件，返回字符串内容。
    :param file_path: 文件路径
    :param encoding: 文件编码，默认为utf-8
    :return: 文件内容， 返回字符串
    """
    assert Path(file_path).exists(), f"文件不存在：{file_path}"
    try:
        with open(file_path, "r", encoding=encoding, errors="ignore") as f:
            return f.read()
    except UnicodeDecodeError as e:
        assert False, f"无法读取文件：{file_path}, 错误信息: {e}"


def parallel_load_txt(files, encoding, max_workers=6, batch_size=6):
    """
    并行处理txt文件
    :param files: 文件列表
    :param max_workers: 最大工作线程数
    :param batch_size: 每批处理的文件数， 当设置很大的时候，即全部文件一起处理时，（前提每个文件都很小），
    """
    total = len(files)
    all_txts = []
    for idx, start in enumerate(range(0, total, batch_size)):
        end = min(start + batch_size, total)
        batch = files[start:end]
        txts = parallel_handle(batch, load_txt, args=(encoding,), max_workers=max_workers)
        if txts:
            all_txts.append("".join(txts))

    return "".join(all_txts) if all_txts else ""


if __name__ == "__main__":

    def process_item(item, factor, add_value):
        return item * factor + add_value

    items = [1, 2, 3, 4]
    factor = 10
    add_value = 5
    args = (factor, add_value)

    # 传递 items, process_item 函数和 args 元组
    results = parallel_handle(items, process_item, args=args)
    print(results)  # 输出 [15, 25, 35, 45]
