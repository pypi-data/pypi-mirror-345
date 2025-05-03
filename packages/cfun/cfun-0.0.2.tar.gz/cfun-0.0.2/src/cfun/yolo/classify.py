from PIL import Image
import numpy as np
import onnxruntime as ort


class YOLOClassifier:
    def __init__(self, model_path, all_names, input_size=(64, 64), providers=["CPUExecutionProvider"]):
        """
        初始化分类器

        :param model_path: ONNX 模型路径
        :param all_names: 类别字典，如 {0: "cat", 1: "dog", ...}
        :param input_size: 模型输入图像尺寸 (W, H)
        :param providers: ONNX 推理后端
        """
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = input_size
        self.all_names = all_names

    def preprocess(self, img_path):
        img = Image.open(img_path).convert("RGB")  # 打开图像并确保为 RGB
        img = img.resize(self.input_size, Image.BILINEAR)  # 调整大小,后面的是一种插值算法
        img = np.array(img).astype(np.float32) / 255.0  # 转为 float32 并归一化
        img = np.transpose(img, (2, 0, 1))  # HWC → CHW
        img = np.expand_dims(img, axis=0)  # 添加 batch 维度 → NCHW
        img = np.ascontiguousarray(
            img
        )  # ascontiguousarray函数将一个内存不连续存储的数组转换为内存连续存储的数组，使得运行速度更快。
        # C连续的。
        return img

    def infer(self, img):
        return self.session.run(None, {self.input_name: img})[0]

    def classify(self, img_path):
        img = self.preprocess(img_path)
        outputs = self.infer(img)
        probs = outputs[0]
        if probs.ndim == 2:
            probs = probs[0]
        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id])
        class_name = self.all_names.get(class_id, f"class_{class_id}")
        return class_id, class_name, confidence


if __name__ == "__main__":

    # from all_name import all_names
    all_names = {0: "cat", 1: "dog"}  # 示例字典

    # 加载自己的模型文件
    onnx_file = "runs/classify/train/weights/best.onnx"
    classifier = YOLOClassifier(model_path=onnx_file, all_names=all_names)

    img_path = "datasets/cls/dingxiang/阿/3e8f115c41_153_66.png"
    class_id, class_name, confidence = classifier.classify(img_path)

    print(f"预测类别: {class_name} (ID: {class_id}), 置信度: {confidence:.4f}")
