import sys
from pathlib import Path

PATH = Path(__file__).resolve().parent
ROOT_PATH = PATH.parent.parent

sys.path.insert(0, str(ROOT_PATH / 'src'))

from track import run

if __name__ == '__main__':
    run()
