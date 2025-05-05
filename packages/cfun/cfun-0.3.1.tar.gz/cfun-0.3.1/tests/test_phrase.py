from cfun.phrase import Phrase
import time


def test_phrase():
    ### 涉及到torch的安装，以及模型的下载，比较麻烦，按需开启
    p = Phrase(corrector="charsimilar")
    fragment = ["下收留情", "手下留情", "人七上下", "情首虾留", "将相王候"]
    stime = time.time()
    for f in fragment:
        reword, matched, isright = p.get_yuxu(f)
        print(f"reword: {reword}, matched: {matched}, isright: {isright}")
    print(f"charsimilar time: {time.time() - stime:.4f}s")

    # p2 = Phrase(corrector="bert")
    # stime = time.time()
    # for f in fragment:
    #     reword, matched, isright = p2.get_yuxu(f)
    #     print(f"reword2: {reword}, matched2: {matched}, isright2: {isright}")
    # print(f"bert time: {time.time() - stime:.4f}s")
    ######## 没有开启纠错器的情况下 ########
    # reword: 收下留情, matched: 手下留情, isright: False
    # reword: 手下留情, matched: 手下留情, isright: True
    # reword: 七上人下, matched: 七上八下, isright: False
    # reword: 情首虾留, matched: , isright: False
    # reword: 候王将相, matched: 帝王将相, isright: False
    ######## 开启纠错器的情况下(bert) ########
    # reword: 收下留情, matched: 手下留情, isright: False
    # reword: 手下留情, matched: 手下留情, isright: True
    # reword: 七上人下, matched: 七上八下, isright: False
    # reword: 情首虾留, matched: , isright: False
    # reword: 王候将相, matched: 王侯将相, isright: False
    ######## 开启纠错器的情况下(charsimilar) ########
    # reword: 收下留情, matched: 手下留情, isright: False
    # reword: 手下留情, matched: 手下留情, isright: True
    # reword: 七上人下, matched: 七上八下, isright: False
    # reword: 情首虾留, matched: , isright: False
    # reword: 王候将相, matched: 王侯将相, isright: False


def test_phrase_cw():
    result = [
        {
            "name": "正",
            "coordinates": [87, 90],
            "points": [[60, 59], [101, 59], [101, 102], [60, 102]],
            "image_width": 300,
            "image_height": 150,
            "rawimgmd5": "f12c826860200e599d0ce8c89f4b10fc",
        },
        {
            "name": "扣",
            "coordinates": [157, 72],
            "points": [[128, 42], [168, 42], [168, 86], [128, 86]],
            "image_width": 300,
            "image_height": 150,
            "rawimgmd5": "f12c826860200e599d0ce8c89f4b10fc",
        },
        {
            "name": "听",
            "coordinates": [50, 39],
            "points": [[24, 22], [65, 22], [65, 68], [24, 68]],
            "image_width": 300,
            "image_height": 150,
            "rawimgmd5": "f12c826860200e599d0ce8c89f4b10fc",
        },
        {
            "name": "埋",
            "coordinates": [27, 112],
            "points": [[9, 89], [49, 89], [49, 125], [9, 125]],
            "image_width": 300,
            "image_height": 150,
            "rawimgmd5": "f12c826860200e599d0ce8c89f4b10fc",
        },
        {
            "name": "梨",
            "coordinates": [252, 66],
            "points": [[222, 49], [264, 49], [264, 97], [222, 97]],
            "image_width": 300,
            "image_height": 150,
            "rawimgmd5": "f12c826860200e599d0ce8c89f4b10fc",
        },
    ]

    p = Phrase(corrector="charsimilar")

    data = p.phrase_cw(result, "听政扣梨")
    print(data)
