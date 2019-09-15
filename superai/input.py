import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.common import GameWindowToTop
from superai.yijianshu import YijianshuInit, KeyInputStgring, RanSleep


def main():
    YijianshuInit()
    # GameWindowToTop()

    if len(sys.argv) > 1:
        RanSleep(3.0)
        KeyInputStgring(sys.argv[1])
    else:
        RanSleep(3.0)
        KeyInputStgring("GGC88zyj")


if __name__ == '__main__':
    main()
