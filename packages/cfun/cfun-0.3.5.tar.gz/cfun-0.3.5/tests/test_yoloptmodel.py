from pathlib import Path

from cfundata import FONT_SIMSUN_PATH
from PIL import Image, ImageDraw, ImageFont

from cfun.yolo.yoloptmodel import YoloPtModel


def test_yoloptmodel():
    image_path = Path(__file__).parent / "images" / "image_detect_01.png"
    yolo = YoloPtModel()
    results = yolo.predict(image_path)
    # Output the result
    print(results)
    # 把结果画框出来
    font_path = str(FONT_SIMSUN_PATH)
    print(f"font_path: {font_path}")
    font_style = ImageFont.truetype(font_path, 20)  # 设置字体和大小
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
        draw.text((x1 - 10, y1 - 10), str(bbox["name"]), fill="blue", font=font_style)
    # 保存图片
    img.save("aaa.png")


if __name__ == "__main__":
    test_yoloptmodel()
