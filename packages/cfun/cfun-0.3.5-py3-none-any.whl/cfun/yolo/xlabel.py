import hashlib
import json
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

from PIL import Image


class XLabel:
    def __init__(
        self,
        image_path: str | Path,
        data: list[dict],
        platform: str = "",
        fixedtimestamp: bool = False,
        filemd5: Optional[str] = None,
        namereplace: dict = None,
    ) -> None:
        """初始化XLabel类

        XLabel类用于生成x-anylabeling格式的json文件

        Args:
            image_path (str): 图片路径, 必须真是存在的文件路径
            data (list[dict]): 标记的坐标，且每个dict中必须包含points这个key， 这个ponits是一个列表，包含四个点的坐标，eg：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            platform (str): 平台名称, 自定义, 默认空字符串
            fixedtimestamp (bool): 是否固定时间戳，默认False, 如果为True，则时间戳为0，否则为当前时间戳
            filemd5 (Optional[str]): 文件的md5值，默认None， 会根据文件自动计算md5值
            namereplace (dict): 替换名称的方式，是一个字典， 其中的key是data中的key，value是模板中shapes字段下的key， 用data中的key来替代模板中的key， 如果没有则不传递

        Example:
            ```python
            image_path = "restoredUnique2/0a19bbddea_乏宙泡瓜色.png"
            data = [{"name": "char1",
                    "points": [[100, 200], [200, 200], [200, 300], [100, 300]],
                    "confidence": 0.9},
                    {"name": "char2",
                    "points": [[300, 400], [400, 400], [400, 500], [300, 500]],
                    "confidence": 0.8}]

            xl = XLabel(
                image_path,
                data,
                platform,
                fixedtimestamp=True,
                namereplace={"name": "description"},
            )
            # 建议json的名字和图片的名字一致（这里是为了测试）
            xl.save_template("template.json") #输出json文件
            ```

        """
        if isinstance(image_path, (str, Path)):
            image_path = Path(image_path)

        if isinstance(data, list):
            data = deepcopy(data)
        assert image_path.exists(), f"image_path: {image_path} 不存在"
        assert image_path.is_file(), f"image_path: {image_path} 不是文件"
        assert image_path.suffix.lower() in [".png", ".jpg", ".jpeg"], (
            f"image_path: {image_path} 不是图片文件"
        )
        assert self._check_data(data, namereplace)
        assert isinstance(fixedtimestamp, bool), (
            f"fixedtimestamp: {fixedtimestamp} 不是布尔值"
        )
        assert filemd5 is None or isinstance(filemd5, str), (
            f"filemd5: {filemd5} 不是字符串"
        )

        self.image_path = image_path
        self.data = data
        self.platform = platform
        self.fixedtimestamp = fixedtimestamp
        self.filemd5 = filemd5 if filemd5 else self._calculate_md5()
        self.namereplace = namereplace
        self.image_width, self.image_height, _ = self._get_image_size()
        self.imagename = self.image_path.name
        self.imagesuffix = self.image_path.suffix

    def _check_data(self, data: list[dict], namereplace: dict) -> bool:
        """
        检查数据是否符合要求
        :param data: 数据
        :param namereplace: 替换名称的方式，是一个字典， 其中的key是data中的key，value是模板中的key， 用data中的key来替代模板中的key， 如果没有则不传递
        :return: 是否符合要求
        """
        if namereplace:
            assert isinstance(namereplace, dict), f"namereplace: {namereplace} 不是字典"
            # key不应该有重复
            assert len(namereplace) == len(set(namereplace.keys())), (
                f"namereplace: {namereplace} 有重复的key"
            )
        assert isinstance(data, list), "参数 data 不是列表"
        assert len(data) > 0, "参数 data 不能为空列表"
        assert all(isinstance(item, dict) for item in data), "参数 data 不是字典列表"

        assert all(
            isinstance(item["points"], list)
            and len(item["points"]) == 4
            and all(
                isinstance(point, list) and len(point) == 2 for point in item["points"]
            )
            for item in data
        ), (
            "参数 data 中的 points 不是列表，或者长度不为4，或者每个点不是列表，或者长度不为2"
        )

        # 如果传递了namereplace， 则检查namereplace中的key是否在data中存在
        if not namereplace:
            return True

        # 所有的key 都应该在data中存在
        for key in namereplace.keys():
            for item in data:
                if key not in item:
                    raise ValueError(f"参数data中不包含key: {key}")

        return True

    def _get_image_size(self) -> tuple[Any, Any, Any]:
        """获取图片的宽高和通道数"""
        image_path = str(self.image_path)
        with Image.open(image_path) as img:
            width, height = img.size
        return width, height, None

    def _calculate_md5(self) -> str:
        """计算文件的 MD5 值"""
        file_path = self.image_path
        hash_md5 = hashlib.md5()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _obtain_attributes(self) -> list[dict]:
        """
        获取模板的属性
        :return: 属性列表
        """
        return {
            "pingtai": self.platform,  # 平台名称
            "timestamp": 0 if self.fixedtimestamp else int(time.time()),  # 时间戳
            "rawimgmd5": self.filemd5,  # 文件的 md5 值
        }

    def _obtain_shapes(self) -> list[dict]:
        oneshape = {
            "kie_linking": [],
            # 标签的类别， 也可以用data中的name来替代
            "label": "1",
            # 置信度, 可选， 可以用data中的confidence来替代
            "score": None,
            # 坐标点, 需要是一个列表， 包含四个点的坐标，
            "points": [],  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            "group_id": None,  # 组ID, 可选
            # 描述信息,对应data中的name
            "description": "",
            "difficult": False,
            "shape_type": "rectangle",
            "flags": {},
            "attributes": {},
        }
        shapes = []
        for item in self.data:
            # 复制模板
            shape = deepcopy(oneshape)
            # 获取描述信息
            if self.namereplace:
                for key, value in self.namereplace.items():
                    if key in item:
                        shape[value] = item[key]

            # 获取置信度
            shape["score"] = item.get("confidence", None)
            # 填充数据
            shape["points"] = item["points"]
            shape["attributes"] = self._obtain_attributes()
            shapes.append(shape)
        return deepcopy(shapes)

    def _generate_template(self) -> dict:
        # 填充模板数据
        template_data = {
            "version": "2.5.4",  # 固定版本
            "flags": {},  # 默认无标记
            "shapes": self._obtain_shapes(),  # 目标框数据
            "imagePath": self.imagename,  # 图片名称
            "imageData": None,  # 默认无图像数据
            "imageHeight": self.image_height,  # 图片高度
            "imageWidth": self.image_width,  # 图片宽度
        }
        return deepcopy(template_data)

    def save_template(self, save_path: str) -> None:
        """保存模板数据到文件

        Args:
            save_path (str): 保存路径
        """
        template_data = self._generate_template()
        with open(str(save_path), "w", encoding="utf-8") as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 测试代码
    image_path = "imgsdata/0a0bd5be39.png"
    data = [
        {
            "name": "char1",
            "points": [[100, 200], [200, 200], [200, 300], [100, 300]],
            "confidence": 0.9,
        },
        {
            "name": "char2",
            "points": [[300, 400], [400, 400], [400, 500], [300, 500]],
            "confidence": 0.8,
        },
    ]

    xl = XLabel(
        image_path,
        data,
        # fixedtimestamp=True,
        # namereplace={"name": "label"},
    )
    # 建议json的名字和图片的名字一致（这里是为了测试）
    xl.save_template("template.json")
