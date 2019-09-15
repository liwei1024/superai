import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.yijianshu import ReleaseAllKey


def main():
    ReleaseAllKey()


if __name__ == '__main__':
    main()
