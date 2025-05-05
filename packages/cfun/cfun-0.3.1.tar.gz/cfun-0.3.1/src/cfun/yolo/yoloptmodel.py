"""
主要是根据 yolo11的目标检测和分类模型，对图片进行检测和分类，返回一个list[dict]，每个元素是一个字典，包含名称和坐标

1. 首先通过检测模型，得到检测框的坐标
2. 然后根据检测框的坐标，裁剪出图片
3. 然后通过分类模型，对裁剪出来的图片进行分类
4. 最后将分类结果和坐标一起返回, 返回一个list[dict]


笔记：创建一个环境
```python
conda create -n yolopy12 python=3.12 -y
conda activate yolopy12
pip install ultralytics
pip install pillow
```
"""

from pathlib import Path

from cfundata import DX_CLS_PT_PATH, DX_DET_PT_PATH
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO  # 可以对实验进行精细化设置


class YoloPtModel:
    """YOLO模型类，用于目标检测和分类

    Attributes:
        INNER_DETECT (str): 内部检测模型路径
        INNER_CLASSIFY (str): 内部分类模型路径
        model (YOLO): YOLO检测模型实例
        model_path (Path): YOLO检测模型路径
        classify_model (YOLO): YOLO分类模型实例
        classify_model_path (Path): YOLO分类模型路径
    """

    INNER_DETECT = DX_DET_PT_PATH  # 内部检测模型
    INNER_CLASSIFY = DX_CLS_PT_PATH  # 内部分类模型

    def __init__(self, detect_model_path: str = "", classify_model_path: str = ""):
        # Load YOLOv8 model for detection and classification
        if not detect_model_path:
            detect_model_path = self.INNER_DETECT
        if not classify_model_path:
            classify_model_path = self.INNER_CLASSIFY
        if isinstance(detect_model_path, Path):
            detect_model_path = str(detect_model_path)
        if isinstance(classify_model_path, Path):
            classify_model_path = str(classify_model_path)
        assert Path(detect_model_path).exists(), (
            f"Detection model not found: {detect_model_path}"
        )
        assert Path(classify_model_path).exists(), (
            f"Classification model not found: {classify_model_path}"
        )
        assert Path(detect_model_path).suffix == ".pt", (
            "Detection model must be a .pt file"
        )
        assert Path(classify_model_path).suffix == ".pt", (
            "Classification model must be a .pt file"
        )

        # 加载模型
        self.model = YOLO(detect_model_path)
        self.model_path = Path(detect_model_path)

        self.classify_model = YOLO(classify_model_path)
        self.classify_model_path = Path(classify_model_path)

    def _predict_detect(self, image_path: str):
        # Predict detection results
        results = self.model.predict(
            source=image_path, conf=0.6, imgsz=640, verbose=False
        )
        xywh = results[0].boxes.xywh.cpu().numpy()
        xyxy = results[0].boxes.xyxy.cpu().numpy()
        return xywh, xyxy

    def _predict_classify(self, image_path: str):
        # Predict classification results
        results = self.classify_model.predict(
            source=image_path, conf=0.6, imgsz=96, verbose=False
        )
        return results

    def predict(self, image_path: str | Path) -> list:
        """根据输入的图片路径进行检测和分类，并返回结果

        Args:
            image_path (str | Path): 图片路径，可以是字符串或Path对象

        Returns:
            list: 检测和分类结果的列表，每个元素是一个字典，包含名称和坐标
            eg:
                [
                    {
                        "name": "object_name", #识别的名称
                        "coordinates": [x, y],
                        ....
                    },
                    ....
                ]

        Example:
            ```python
            from cfundata import FONT_SIMSUN_PATH
            yolo = YoloPtModel()
            image_path = "assets/image_detect_01.png"
            results = yolo.predict(image_path)
            print(results)
            # 把结果画框出来
            font_style = ImageFont.truetype(FONT_SIMSUN_PATH, 20)
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            for _idx, bbox in enumerate(results):
                points = bbox["points"]
                x1, y1 = points[0]
                x2, y2 = points[2]
                draw.rectangle((x1, y1, x2, y2), outline="red", width=3)
                draw.text((x1 - 10, y1 - 10), str(bbox["name"]), font=font_style, fill="blue")
            img.save("aaa.png")
            ```
        """
        if isinstance(image_path, Path):
            image_path = str(image_path)
        assert Path(image_path).exists(), f"Image not found: {image_path}"
        assert Path(image_path).suffix in [".jpg", ".png", ".jpeg"], (
            f"Unsupported image format: {image_path}"
        )
        assert Path(image_path).is_file(), f"Image path is not a file: {image_path}"
        # Step 1: Perform object detection
        xywh, xyxy = self._predict_detect(image_path)

        # Step 2: Load image for cropping
        img = Image.open(image_path)
        results = []

        # Step 3: For each detected box, crop the image and classify
        for _i, box in enumerate(xyxy.tolist()):
            x1, y1, x2, y2 = map(int, box)  # Convert to integers
            cropped_img = img.crop(
                (x1, y1, x2, y2)
            )  # Crop the image using the bounding box

            # cropped_img.save(f"temp_cropped_{i}.png")  # Save the cropped image temporarily

            # Step 4: Perform classification on the cropped image
            classify_results = self._predict_classify(cropped_img)

            # Step 5: Process classification results
            assert len(classify_results) == 1, (
                "Classification result should be a single output."
            )
            r = classify_results[0]
            all_names = r.names  # All class names
            top1 = r.probs.top1  # Index of the top prediction
            top1name = all_names[top1]  # Top prediction name
            top1conf = r.probs.top1conf.item()  # Top prediction confidence

            # Step 6: Store the result
            results.append(
                {
                    "name": top1name,  # name即对应的分类名称
                    "confidence": round(top1conf, 4),  # Confidence score
                    "coordinates": [(x1 + x2) / 2, (y1 + y2) / 2],
                    "points": [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],  # 四个点坐标
                }
            )

        return results


if __name__ == "__main__":
    from cfundata import FONT_SIMSUN_PATH

    yolo = YoloPtModel()
    image_path = "assets/image_detect_01.png"
    results = yolo.predict(image_path)
    print(results)
    # 把结果画框出来

    font_style = ImageFont.truetype(FONT_SIMSUN_PATH, 20)  # 设置字体和大小
    img = Image.open(image_path)  # 打开图片
    draw = ImageDraw.Draw(img)  # 创建一个可以在图片上绘制的对象(相当于画布)
    # 遍历每个框，画框
    for _idx, bbox in enumerate(results):
        points = bbox["points"]
        x1, y1 = points[0]
        x2, y2 = points[2]
        # 画框, outline参数用来设置矩形边框的颜色
        draw.rectangle((x1, y1, x2, y2), outline="red", width=3)
        # 写字 (偏移一定的距离)
        draw.text((x1 - 10, y1 - 10), str(bbox["name"]), font=font_style, fill="blue")
    # 保存图片
    img.save("aaa.png")
