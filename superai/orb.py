import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import cv2

from superai.screenshots import WindowCaptureToMem


def main():
    orb = cv2.ORB_create()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    manImg = cv2.imread("E:/win/tmp/capture/palading.bmp")
    manKp, manDes = orb.detectAndCompute(manImg, None)

    while True:
        sceneImg = WindowCaptureToMem("地下城与勇士", "地下城与勇士")
        sceneKp, scensDes = orb.detectAndCompute(sceneImg, None)

        matches = bf.match(manDes, scensDes)
        matches = sorted(matches, key=lambda x: x.distance)
        resultImg = cv2.drawMatches(manImg, manKp, sceneImg, sceneKp, matches[:25], sceneImg, flags=2)

        cv2.imshow('my img', resultImg)

        if (cv2.waitKey(30) & 0xFF) in [ord('q'), 27]:
            break

        time.sleep(0.1)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
