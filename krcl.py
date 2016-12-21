import requests


def stream():
    req = requests.get(url='http://stream.xmission.com/krcl-high',
                       stream=True, timeout=(3.5, 15))
    for block in req.iter_content(16000):
        if block:
            yield block
