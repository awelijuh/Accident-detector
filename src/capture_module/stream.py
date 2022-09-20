import cv2
import pafy

from config.provider import get_conf

conf = get_conf().capture


def get_stream():
    url = conf.stream_url
    print(conf)
    if 'youtube.com' in url:
        youtube_quality = conf.get('youtube_quality', '1080')
        video = pafy.new(url)
        streams = [v for v in video.streams if v.extension == 'mp4' and v.quality.endswith(youtube_quality)]

        # best = video.getworst(preftype="mp4")
        r_url = streams[0].url
    else:
        r_url = url

    return cv2.VideoCapture(r_url)
