import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import cv2

from superai.screenshots import WindowCaptureToMem


def main():
    if len(sys.argv) < 2:
        print("usage: {} png".format(sys.argv[0]))
        exit(0)

    findImg = sys.argv[1]

    sift = cv2.xfeatures2d.SIFT_create()

    findImg = cv2.imread(findImg)
    findKp, findDes = sift.detectAndCompute(findImg, None)

    while True:
        sceneImg = WindowCaptureToMem("地下城与勇士", "地下城与勇士")
        sceneKp, scensDes = sift.detectAndCompute(sceneImg, None)

        indexParams = dict(algorithm=0, trees=5)
        searchParams = dict(checks=50)
        flann = cv2.FlannBasedMatcher(indexParams, searchParams)

        matches = flann.knnMatch(findDes, scensDes, k=2)
        matchesMask = [[0, 0] for i in range(len(matches))]

        for i, (m, n) in enumerate(matches):
            if m.distance < 0.7 * n.distance:
                matchesMask[i] = [1, 0]

        drawParams = dict(matchColor=(0, 255, 0),
                          singlePointColor=(255, 0, 0),
                          matchesMask=matchesMask,
                          flags=0)

        resultImg = cv2.drawMatchesKnn(findImg, findKp, sceneImg, sceneKp, matches, None, **drawParams)

        cv2.imshow('my img', resultImg)

        if (cv2.waitKey(30) & 0xFF) in [ord('q'), 27]:
            break

        time.sleep(0.1)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
