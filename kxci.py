import requests
import time
import re

URL = 'http://kxci.streamon.fm/hls/KXCI-32k.m3u8?Please=SirCanIHaveSomeMore'
STREAM_BASE = 'http://kxci.streamon.fm/hls/stream/'
TARGET_DURATION = re.compile(r'#EXT-X-TARGETDURATION:(\d*)')
MEDIA_SEQUENCE = re.compile(r'#EXT-X-MEDIA-SEQUENCE:(\d*)')


def stream():
    req = requests.get(url=URL)
    for line in req.iter_lines():
        if line.startswith('http'):
            m3u8_url = line
            break

    last_seq = 0
    while True:
        req = requests.get(url=m3u8_url)
        t = time.time()
        dur = int(TARGET_DURATION.search(req.text).group(1))
        seq = int(MEDIA_SEQUENCE.search(req.text).group(1))
        for line in req.iter_lines():
            if not line.startswith('#'):
                if seq <= last_seq:
                    continue
                seg_url = STREAM_BASE + line
                seg_req = requests.get(url=seg_url)
                if seg_req.status_code == 200:
                    yield seg_req.content
                    last_seq = seq
                    seq += 1
        time.sleep(dur - (time.time() - t))
