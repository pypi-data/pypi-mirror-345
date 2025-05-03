from PIL import Image, ImageDraw, ImageFont
import numpy as np
import onnxruntime as ort
from pathlib import Path


class YOLODetector:
    def __init__(self, model_path, input_size=(640, 640), providers=["CPUExecutionProvider"]):
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = input_size

    def letterbox(self, img, new_shape=(640, 640), color=(114, 114, 114), scaleup=True):
        shape = img.size  # (width, height)
        r = min(new_shape[0] / shape[1], new_shape[1] / shape[0])
        if not scaleup:
            r = min(r, 1.0)

        new_unpad = (int(round(shape[0] * r)), int(round(shape[1] * r)))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        dw /= 2
        dh /= 2

        img = img.resize(new_unpad, Image.BILINEAR)
        new_img = Image.new("RGB", new_shape, color)
        new_img.paste(img, (int(dw), int(dh)))
        return new_img, r, (dw, dh)

    def preprocess(self, img_path):
        img0 = Image.open(img_path).convert("RGB")
        img, ratio, (dw, dh) = self.letterbox(img0, self.input_size)
        img = np.array(img).astype(np.float32) / 255.0  # HWC, RGB
        img = np.transpose(img, (2, 0, 1))[np.newaxis, ...]  # NCHW
        return img, img0, ratio, dw, dh

    def infer(self, img):
        return self.session.run(None, {self.input_name: img})[0]

    def detect(self, img_path, conf_thres=0.25):
        img, img0, ratio, dw, dh = self.preprocess(img_path)
        preds = self.infer(img)[0]

        detections = []
        for det in preds:
            x1, y1, x2, y2, conf, cls = det
            if conf < conf_thres:
                continue

            x1 = (x1 - dw) / ratio
            y1 = (y1 - dh) / ratio
            x2 = (x2 - dw) / ratio
            y2 = (y2 - dh) / ratio

            detections.append({"box": [int(x1), int(y1), int(x2), int(y2)], "conf": float(conf), "cls": int(cls)})

        return detections, img0

    def draw_results(self, img, detections, save_path="result.png"):
        draw = ImageDraw.Draw(img)
        for det in detections:
            box = det["box"]
            conf = det["conf"]
            cls = det["cls"]
            x1, y1, x2, y2 = box
            draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=2)
            draw.text((x1, y1 - 10), f"{cls} {conf:.2f}", fill=(255, 0, 0))
        img.save(save_path)


if __name__ == "__main__":
    onnx_file = "runs/detect/train/weights/best.onnx"
    detector = YOLODetector(onnx_file)

    img_path1 = "datasets/detect/dingxiang/images/test/0a2c95e787_听埋扣梨正.png"
    detections1, original_img1 = detector.detect(img_path1)
    for det in detections1:
        print(det)
    detector.draw_results(original_img1, detections1, save_path="result1.png")

    img_path2 = "datasets/detect/dingxiang/images/test/0a3d15e3bf_么旺泥草行.png"
    detections2, original_img2 = detector.detect(img_path2)
    for det in detections2:
        print(det)
    detector.draw_results(original_img2, detections2, save_path="result2.png")
