import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.common import GameWindowToTop
from superai.yijianshu import YijianshuInit, KeyInputString, RanSleep


def main():
    if not YijianshuInit():
        exit(0)
    # GameWindowToTop()

    if len(sys.argv) > 1:
        RanSleep(3.0)
        KeyInputString(sys.argv[1])
    else:
        RanSleep(3.0)
        KeyInputString("GGC88zyj")


if __name__ == '__main__':
    main()
