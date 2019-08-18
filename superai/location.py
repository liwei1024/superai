import os
import sys

from superai.flannfind import Picture, GetImgDir

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)


locationAierwenfangxian = Picture(GetImgDir() + "/location_aierwenfangxian.png")


class Location:
    def __init__(self):
        pass

    def get(self):
        if locationAierwenfangxian.Match():
            return "艾尔文防线"

        return ""



def main():
    pass


if __name__ == '__main__':
    main()
