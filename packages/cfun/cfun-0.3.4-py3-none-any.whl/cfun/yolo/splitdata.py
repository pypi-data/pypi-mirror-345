import os
import shutil
from pathlib import Path

from sklearn.model_selection import train_test_split


def _create_directories(base_imgpath: str | Path, base_txtpath: str | Path):
    """Create the necessary directories for train, val, and test sets."""
    Path(base_imgpath).mkdir(parents=True, exist_ok=True)
    Path(base_txtpath).mkdir(parents=True, exist_ok=True)

    for split in ["train", "val", "test"]:
        os.makedirs(Path(base_imgpath) / split, exist_ok=True)
        os.makedirs(Path(base_txtpath) / split, exist_ok=True)


def _copy_files(
    file_list: list[str],
    imgpath: str,
    txtpath: str,
    new_imgpath: str,
    new_txtpath: str,
    postfix: str,
    subdir: str,
):
    """Copy image and label files for each split (train, val, test)."""
    for file in file_list:
        try:
            img_source = Path(imgpath) / f"{file}{postfix}"
            txt_source = Path(txtpath) / f"{file}.txt"
            assert img_source.exists(), f"Image file {img_source} does not exist."
            assert txt_source.exists(), f"Label file {txt_source} does not exist."

            img_dest = Path(new_imgpath) / subdir / f"{file}{postfix}"
            txt_dest = Path(new_txtpath) / subdir / f"{file}.txt"

            shutil.copy2(img_source, img_dest)
            shutil.copy2(txt_source, txt_dest)
        except Exception as e:
            print(f"Error copying {file}: {e}")


def splitdata(
    imgpath: str | Path,
    txtpath: str | Path,
    new_imgpath: str | Path,
    new_txtpath: str | Path,
    val_size: float = 0.1,
    test_size: float = 0.1,
    postfix: str = ".png",
) -> None:
    """将数据集拆分为训练集、val集和测试集，并相应地复制文件。(主要用于yolo目标检测数据的划分)

    主要用于yolo目标检测数据的划分，分成训练集、验证集和测试集。

    !!! note
        对于分类数据， 官方提供了另外的函数可以直接划分
        ```python
        from ultralytics.data.split import split_classify_dataset
        ```

    Args:
        imgpath (str | Path): 原始图片路径的根目录 （这个目录下包含了要处理的图片）
        txtpath (str | Path): 原始标签路径的根目录 （txt文件， 图片文件和txt文件的stem要一样，没有重复样本且数量也要一致，否则可能报错）
        new_imgpath (str | Path): 新的图片路径
        new_txtpath (str | Path): 新的标签路径
        val_size (float, optional): 验证集所占比例. Defaults to 0.1.
        test_size (float, optional): 测试集所占比例. Defaults to 0.1.
        postfix (str, optional): 图片后缀名. Defaults to ".png".

    Raises:
        AssertionError: 如果原始图片路径或标签路径不存在，抛出异常。
        AssertionError: 如果txt文件和图片文件的stem不一致 或者数量不一致，抛出异常。
        ValueError: 如果val_size和test_size不在0到1之间，抛出异常。
        ValueError: 如果val_size + test_size >= 1，抛出异常。

    Example:
        ```python
        from src.cfun.yolo.splitdata import splitdata
        imgpath = "imgsdata"  #图片的路径
        txtpath = "detect"  #标签的路径
        new_imgpath = "./imgs_split/train/images"  #新的图片路径
        new_txtpath = "./imgs_split/train/labels" #新的标签路径
        splitdata(imgpath, txtpath, new_imgpath, new_txtpath)
        ```
    """
    if not (0 <= val_size <= 1):
        raise ValueError("val_size must be between 0 and 1")
    if not (0 <= test_size <= 1):
        raise ValueError("test_size must be between 0 and 1")
    if val_size + test_size >= 1:
        raise ValueError("val_size + test_size must be less than 1")
    if isinstance(imgpath, str):
        imgpath = Path(imgpath)
    if isinstance(txtpath, str):
        txtpath = Path(txtpath)
    if isinstance(new_imgpath, str):
        new_imgpath = Path(new_imgpath)
    if isinstance(new_txtpath, str):
        new_txtpath = Path(new_txtpath)

    assert imgpath.is_dir() and txtpath.exists(), (
        f"Image path {imgpath} is not a directory or label path {txtpath} does not exist."
    )
    assert txtpath.is_dir() and imgpath.exists(), (
        f"Label path {txtpath} is not a directory or image path {imgpath} does not exist."
    )

    #  计算验证集所占的比例
    _val_size = val_size / (1 - test_size)

    # 创建必要的目录
    _create_directories(new_imgpath, new_txtpath)

    # 遍历txtpath 下的所有txt
    names = [i.stem for i in txtpath.rglob("*.txt") if i.is_file()]

    # names 未重复
    assert len(names) == len(set(names)), (
        f"Label files in {txtpath} are not unique. Please check the files."
    )

    train, test = train_test_split(
        names, test_size=test_size, shuffle=True, random_state=0
    )
    train, val = train_test_split(
        train, test_size=_val_size, shuffle=True, random_state=0
    )

    s0 = f"train set size: {len(train)} val set size: {len(val)} test set size: {len(test)}"
    print(s0)

    # Copy the files to the appropriate directories
    _copy_files(
        train, imgpath, txtpath, new_imgpath, new_txtpath, postfix, subdir="train"
    )
    _copy_files(val, imgpath, txtpath, new_imgpath, new_txtpath, postfix, subdir="val")
    _copy_files(
        test, imgpath, txtpath, new_imgpath, new_txtpath, postfix, subdir="test"
    )

    return None


if __name__ == "__main__":
    imgpath = "imgsdata"  # 图片的路径
    txtpath = "detect"  # 标签的路径
    new_imgpath = "./imgs_split/train/images"  # 新的图片路径
    new_txtpath = "./imgs_split/train/labels"  # 新的标签路径
    splitdata(imgpath, txtpath, new_imgpath, new_txtpath)
