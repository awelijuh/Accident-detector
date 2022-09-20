import sys
from pathlib import Path

PATH = Path(__file__).resolve().parent
ROOT_PATH = PATH.parent.parent

sys.path.insert(0, str(ROOT_PATH / 'src'))

from capturer import Capturer

if __name__ == '__main__':
    r = Capturer()
    r.start_road()
    print("Video stop")
