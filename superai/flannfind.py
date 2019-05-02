import sys
import os
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import cv2

from superai.screenshots import WindowCaptureToMem

MIN_MATCH_COUNT = 10

def main():
    if len(sys.argv) < 2:
        print("usage: {} png".format(sys.argv[0]))
        exit(0)

    # img1 = cv2.imread(sys.argv[1], 0)


if __name__ == "__main__":
    main()
