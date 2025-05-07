from pathlib import Path

from cfundata import DX_CLS_ONNX_PATH, DX_DET_ONNX_PATH

from cfun.yolo.classify import YOLOClassifier
from cfun.yolo.detect import YOLODetector


def test_detect():
    onnx_path = DX_DET_ONNX_PATH
    print(f"onnx_path: {onnx_path}")
    img_path = Path(__file__).parent / "images" / "image_detect_01.png"
    detector = YOLODetector(onnx_path)

    detections, original_img = detector.detect(img_path)
    for det in detections:
        print(det)
    detector.draw_results(original_img, detections, save_path="result1.png")


def test_classify():
    onnx_file = DX_CLS_ONNX_PATH
    print(f"onnx_file: {onnx_file}")
    img_path = Path(__file__).parent / "images" / "image_cls_01.png"
    # from all_name import all_names
    all_names = {
        0: "cat",
        1: "dog",
        1307: "阿",
    }  # 示例字典

    classifier = YOLOClassifier(model_path=onnx_file, all_names=all_names)

    class_id, class_name, confidence = classifier.classify(img_path)

    print(f"预测类别: {class_name} (ID: {class_id}), 置信度: {confidence:.4f}")
    assert class_id == 1307, "分类结果不正确"
