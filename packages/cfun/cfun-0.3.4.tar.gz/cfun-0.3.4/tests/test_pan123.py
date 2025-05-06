import os

from cfun.pan123 import Pan123openAPI


def test_pan123():
    access_token = os.environ.get("PAN123TOKEN")
    pan123 = Pan123openAPI()
    # pan123.refresh_access_token(access_token)
    # file_id = pan123.upload(
    #     "/home/ubuntu/Desktop/yolo/dingxiang/runs13000/classify/train/weights/epoch150.pt",
    #     "epoch150.pt",
    #     0,
    # )
    # print(file_id)
