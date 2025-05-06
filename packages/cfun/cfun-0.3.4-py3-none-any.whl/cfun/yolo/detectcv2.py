from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np
import onnxruntime as ort


class YOLODetector:
    """yolo检测器

    Attributes:
        session: ONNX Runtime inference session.
        input_name: Name of the input tensor.
        input_size: Size of the input image.
    """

    def __init__(
        self,
        model_path: str | Path,
        input_size: tuple[int, int] = (640, 640),
        providers: Optional[list] = None,
    ):
        """初始化

        Args:
            model_path (str or Path): Path to the ONNX model file.
            input_size (tuple): Size of the input image (width, height).
            providers (list): List of execution providers for ONNX Runtime.

        """
        if providers is None:
            providers = ["CPUExecutionProvider"]
        if isinstance(model_path, Path):
            model_path = str(model_path)

        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = input_size

    def _letterbox(
        self,
        img: np.ndarray,
        new_shape: tuple[int, int] = (640, 640),
        color: tuple[int, int, int] = (114, 114, 114),
        auto: bool = False,
        scaleFill: bool = False,
        scaleup: bool = True,
    ):
        """重新调整图像大小，保持纵横比并填充空白区域

        Args:
            img (np.ndarray): Input image.
            new_shape (tuple): New shape for the image (width, height).
            color (tuple): Color for the padding (R, G, B).
            auto (bool): Whether to automatically adjust the aspect ratio.
            scaleFill (bool): Whether to fill the entire new shape.
            scaleup (bool): Whether to scale up the image if it's smaller than new_shape.

        Returns:
            tuple: Tuple containing the resized image, the resize ratio, and the padding (dw, dh).
        """
        shape = img.shape[:2]  # current shape [height, width]
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:
            r = min(r, 1.0)

        new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        dw /= 2
        dh /= 2

        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
        )

        return img, r, (dw, dh)

    def _preprocess(self, img_path):
        img0 = cv2.imread(img_path)
        img, ratio, (dw, dh) = self._letterbox(img0, self.input_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))[np.newaxis, ...]  # NCHW
        img = np.ascontiguousarray(img)  # 转为连续内存块
        return img, img0, ratio, dw, dh

    def _infer(self, img):
        """推理"""
        return self.session.run(None, {self.input_name: img})[0]

    def detect(
        self, img_path: Union[str, Path], conf_thres: float = 0.65
    ) -> tuple[list, np.ndarray]:
        """检测图像中的物体

        Args:
            img_path (Union[str, Path]): Path to the input image.
            conf_thres (float): Confidence threshold for filtering detections.

        Returns:
            tuple: List of detections and the original image.

        Example:
            ```python
            from cfundata import DX_DET_ONNX_PATH
            detector = YOLODetector(DX_DET_ONNX_PATH)
            img_path = "assets/image_detect_01.png"
            detections, original_img = detector.detect(img_path)
            # 在原图上绘制检测框
            for det in detections:
                print(det)
                box = det["box"]
                conf = det["conf"]
                cls = det["cls"]
                x1, y1, x2, y2 = box
                cv2.rectangle(original_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    original_img,
                    f"{int(cls)} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    1,
                )
            # 存储结果
            cv2.imwrite("result2.png", original_img)
            ```
        """

        img, img0, ratio, dw, dh = self._preprocess(img_path)
        preds = self._infer(img)[0]  # (num_dets, 6): x1, y1, x2, y2, conf, cls

        detections = []
        for det in preds:
            x1, y1, x2, y2, conf, cls = det
            if conf < conf_thres:
                continue

            # 还原回原图尺寸
            x1 = (x1 - dw) / ratio
            y1 = (y1 - dh) / ratio
            x2 = (x2 - dw) / ratio
            y2 = (y2 - dh) / ratio

            detections.append(
                {
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "conf": float(conf),
                    "cls": int(cls),
                }
            )

        return detections, img0


if __name__ == "__main__":
    from cfundata import DX_DET_ONNX_PATH

    detector = YOLODetector(DX_DET_ONNX_PATH)

    img_path = "assets/image_detect_01.png"
    detections, original_img = detector.detect(img_path)

    for det in detections:
        print(det)
        box = det["box"]
        conf = det["conf"]
        cls = det["cls"]
        x1, y1, x2, y2 = box
        cv2.rectangle(original_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            original_img,
            f"{int(cls)} {conf:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            1,
        )
    # 存储结果
    cv2.imwrite("result2.png", original_img)
