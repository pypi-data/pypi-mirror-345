import cv2
import numpy as np
import onnxruntime as ort


class YOLODetector:
    def __init__(self, model_path, input_size=(640, 640), providers=["CPUExecutionProvider"]):
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = input_size

    def letterbox(self, img, new_shape=(640, 640), color=(114, 114, 114), auto=False, scaleFill=False, scaleup=True):
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
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

        return img, r, (dw, dh)

    def preprocess(self, img_path):
        img0 = cv2.imread(img_path)
        img, ratio, (dw, dh) = self.letterbox(img0, self.input_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))[np.newaxis, ...]  # NCHW
        img = np.ascontiguousarray(img)  # 转为连续内存块
        return img, img0, ratio, dw, dh

    def infer(self, img):
        return self.session.run(None, {self.input_name: img})[0]

    def detect(self, img_path, conf_thres=0.25):
        img, img0, ratio, dw, dh = self.preprocess(img_path)
        preds = self.infer(img)[0]  # (num_dets, 6): x1, y1, x2, y2, conf, cls

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

            detections.append({"box": [int(x1), int(y1), int(x2), int(y2)], "conf": float(conf), "cls": int(cls)})

        return detections, img0


if __name__ == "__main__":
    onnx_file = "runs/detect/train/weights/best.onnx"
    img_path = "datasets/detect/dingxiang/images/test/0a2c95e787_听埋扣梨正.png"
    detector = YOLODetector(onnx_file)

    detections, original_img = detector.detect(img_path)

    for det in detections:
        print(det)
        box = det["box"]
        conf = det["conf"]
        cls = det["cls"]
        x1, y1, x2, y2 = box
        cv2.rectangle(original_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            original_img, f"{int(cls)} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1
        )
    # 存储结果
    cv2.imwrite("result.png", original_img)

    img_path2 = "datasets/detect/dingxiang/images/test/0a3d15e3bf_么旺泥草行.png"
    detections2, original_img2 = detector.detect(img_path2)
    for det in detections2:
        print(det)
