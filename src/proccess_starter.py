from multiprocessing import Process

import uvicorn

from capture_module.capturer import Capturer
from detect_module import track


def start_capture():
    cap = Capturer()
    cap.start_road()


def start_api():
    uvicorn.run("api_module.api:app")


if __name__ == '__main__':
    capture_process = Process(target=start_capture, daemon=True)
    detect_process = Process(target=track.run, daemon=True)
    api_process = Process(target=start_api, daemon=True)

    capture_process.start()
    detect_process.start()
    api_process.start()

    capture_process.join()
    detect_process.join()
    api_process.join()
