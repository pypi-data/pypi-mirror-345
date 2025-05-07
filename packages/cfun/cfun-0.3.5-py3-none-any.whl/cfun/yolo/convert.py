"""
通过json文件把 目标 生成yolo格式的txt文件， 进行目标检测数据分类，按指定的key进行分类， 比如： label 分

也可以直接用xlabeling 这些工具直接导出txt文件， 但需要手动划分数据集
"""

import json
import re
import shutil
from pathlib import Path

from PIL import Image


def json_to_yolo_txt(
    json_dir: Path | str,
    label_key: str,
    class_mapping_file: Path | str,
    output_dir: Path | str,
    image_dir: Path | str = None,
    image_suffix: str = ".png",
    force_overwrite: bool = False,
    ischeck: bool = True,
) -> None:
    """将 XLabeling 标注的 JSON 文件转换为 YOLO 格式的 TXT 文件。

    Args:
        json_dir (Path | str): JSON 标注文件所在目录
        label_key (str): 用于分类的键,如 "label"
        class_mapping_file (Path | str): 类别名称映射文件路径
        output_dir (Path | str): 输出的 TXT 文件目录
        image_dir (Path | str): 图像文件所在目录, 默认 None
        image_suffix (str): 图像文件后缀名, 默认 ".png"
        force_overwrite (bool): 是否强制覆盖输出目录, 默认 False
        ischeck (bool): 是否检查图像文件是否存在, 默认 True, 如果为True, 则会根据json文件的名称去检查图像文件是否存在, 如果不存在则报错

    Returns:
        None

    Example:
        ```python
        from cfun.yolo.convert import json_to_yolo_txt
        json_dir = "imgsdata/xlabeljson"
        label_key = "label"
        class_mapping_file = "class.txt"
        output_dir = "Label"
        image_dir = "imgsdata"
        image_suffix = ".png"
        force_overwrite = True
        json_to_yolo_txt(
            json_dir,
            label_key,
            class_mapping_file,
            output_dir,
            image_dir,
            image_suffix,
            force_overwrite,
        )
        ```
    """
    json_dir = Path(json_dir)
    if ischeck:
        image_dir = Path(image_dir)
    class_mapping_file = Path(class_mapping_file)
    output_dir = Path(output_dir)

    # 读取类别映射文件
    if class_mapping_file.suffix != ".txt":
        raise ValueError(f"Unsupported class mapping file format: {class_mapping_file}")

    with open(class_mapping_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # 验证文件内容有效性
    if not all(":" in line for line in lines):
        raise ValueError(f"Invalid format in class mapping file: {class_mapping_file}")

    class_mapping = {i: line.split(":")[1].strip() for i, line in enumerate(lines)}
    for i, line in enumerate(lines):
        assert int(line.split(":")[0].strip()) == i, (
            f"Line {i} in class mapping does not match index"
        )

    # 管理输出目录
    if output_dir.exists():
        if force_overwrite:
            shutil.rmtree(output_dir)
            print(f"[警告] 输出目录已存在，已被删除: {output_dir}")
        else:
            raise FileExistsError(f"Output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取 JSON 文件和对应的图像文件
    json_files = list(json_dir.rglob("*.json"))
    if ischeck:
        image_files = [
            image_dir / (json_file.stem + image_suffix) for json_file in json_files
        ]

        for image_path in image_files:
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
        # 检查数量是否一致
        # if len(json_files) != len(image_files):
        #     raise ValueError(
        #         f"Number of JSON files ({len(json_files)}) does not match number of image files ({len(image_files)})"
        #     )
    for idx, json_file in enumerate(json_files):
        if idx % 100 == 0 or idx == len(json_files) - 1:
            print(f"Processing {idx}/{len(json_files)}")

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_width, image_height = data["imageWidth"], data["imageHeight"]
        annotations = []

        for shape in data["shapes"]:
            points = shape["points"]
            label = shape[label_key]

            # YOLO assumes (x_center, y_center, width, height)
            x1, y1, x2, y2 = map(
                int, [points[0][0], points[0][1], points[2][0], points[2][1]]
            )
            assert x1 < x2 and y1 < y2, f"Invalid box: {x1, y1, x2, y2}"

            x_center = (x1 + x2) / 2 / image_width
            y_center = (y1 + y2) / 2 / image_height
            width = (x2 - x1) / image_width
            height = (y2 - y1) / image_height

            annotations.append(
                {
                    "label": label,
                    "x_center": x_center,
                    "y_center": y_center,
                    "width": width,
                    "height": height,
                }
            )

        txt_file = output_dir / (json_file.stem + ".txt")

        with open(txt_file, "w", encoding="utf-8") as f:
            for ann in annotations:
                label_name = ann["label"]
                label_id = next(
                    (k for k, v in class_mapping.items() if v == label_name), None
                )
                assert label_id is not None, (
                    f"Label '{label_name}' not in class mapping."
                )

                f.write(
                    f"{label_id} {ann['x_center']:.6f} {ann['y_center']:.6f} "
                    f"{ann['width']:.6f} {ann['height']:.6f}\n"
                )


def crop_images(
    json_dir: Path | str,
    image_dir: Path | str,
    image_suffix: str = ".png",
    category_key: str = "label",
    isremove_chinese: bool = True,
    output_dir: Path | str = "cropped",
    force_overwrite: bool = False,
    ischeck: bool = True,
) -> None:
    """
    根据 JSON 标注文件裁剪图像，并根据指定字段（如 label ）分类保存。

    Args:
        json_dir (Path | str): 存放 JSON 标注文件的目录
        image_dir (Path | str): 原始图像文件所在目录. json文件和图像文件同名,
        image_suffix (str): 图像文件后缀名, 默认 ".png"
        category_key (str): 用于分类图像的字段（例如 "label"）
        isremove_chinese (bool): 裁剪后的图片是否移除中文字符和下划线_, 默认 True， 这里的下划线是指原来文件名中的下划线，因为裁剪后的图片文件名中会有下划线
        output_dir (Path | str): 裁剪后图像的输出目录, 默认 "cropped"
        force_overwrite (bool): 是否强制覆盖输出目录, 默认 False, 如果为True, 则会删除原有的输出目录
        ischeck (bool): 是否检查图像文件是否存在, 默认 True, 如果为True, 检查json文件数量和图像文件数量是否一致, 如果不一致则报错

    Returns:
        None

    Example:
        ```python
        from cfun.yolo.convert import crop_images
        crop_images(
            json_dir="imgsdata/xlabeljson",
            image_dir="imgsdata",
            category_key="description",
            output_dir="cropped",  # 输出的裁剪图片的路径
            force_overwrite=True,  # 是否强制覆盖输出目录
        )
        ```
    """

    json_dir = Path(json_dir)
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)
    if output_dir.exists():
        if force_overwrite:
            shutil.rmtree(output_dir)
            print(f"[警告] 输出目录已存在，已被删除: {output_dir}")
        else:
            raise FileExistsError(f"Output directory already exists: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    # 查找所有 JSON 文件
    json_files = list(json_dir.rglob("*.json"))
    image_files = [
        image_dir / (json_file.stem + image_suffix) for json_file in json_files
    ]

    # 验证图像和标注文件是否存在
    for image_file in image_files:
        assert image_file.exists(), f"Image file does not exist: {image_file}"
    for json_file in json_files:
        assert json_file.exists(), f"JSON file does not exist: {json_file}"
    if ischeck:
        # 检查数量是否一致
        if len(json_files) != len(image_files):
            raise ValueError(
                f"Number of JSON files ({len(json_files)}) does not match number of image files ({len(image_files)})"
            )

    for idx, json_file in enumerate(json_files):
        if idx % 100 == 0 or idx == len(json_files) - 1:
            print(f"Processing {idx}/{len(json_files)}")

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_file = image_dir / (json_file.stem + ".png")
        image = Image.open(image_file)

        if image is None:
            print(f"Failed to load image: {image_file}")
            continue

        for shape in data["shapes"]:
            points = shape["points"]
            category = shape[category_key]

            x1, y1 = int(points[0][0]), int(points[0][1])
            x2, y2 = int(points[2][0]), int(points[2][1])
            assert x1 < x2 and y1 < y2, f"Invalid coordinates: {x1}, {y1}, {x2}, {y2}"

            cropped_image = image.crop((x1, y1, x2, y2))

            base_name = json_file.stem
            if isremove_chinese:
                # 移除中文字符
                base_name = re.sub(r"[\u4e00-\u9fa5_]", "", base_name)

            file_name = f"{base_name}_{x1}_{y1}{image_suffix}"
            output_path = Path("cropped") / category / file_name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cropped_image.save(output_path)


if __name__ == "__main__":
    pass
    # json_dir = "imgsdata/xlabeljson"
    # label_key = "label"  # 指定分类的key
    # class_mapping_file = "class.txt"  # 输入类别名称的映射（是一个文件,txt文件）
    # output_dir = "Label"  # 输出的txt文件的路径

    # image_dir = "imgsdata"
    # image_suffix = ".png"
    # force_overwrite = True  # 是否强制覆盖输出目录
    # json_to_yolo_txt(
    #     json_dir=json_dir,
    #     label_key=label_key,
    #     class_mapping_file=class_mapping_file,
    #     output_dir=output_dir,
    #     image_dir=image_dir,
    #     image_suffix=image_suffix,
    #     force_overwrite=force_overwrite,
    # )

    # crop_images(
    #     json_dir="imgsdata/xlabeljson",
    #     image_dir="imgsdata",
    #     category_key="description",
    #     output_dir="cropped",  # 输出的裁剪图片的路径
    #     force_overwrite=True,  # 是否强制覆盖输出目录
    # )
