import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import cv2
import numpy as np
from datetime import datetime
from superai.screenshots import WindowCaptureToMem

MIN_MATCH_COUNT = 10


def Log(s):
    print("%s %s" % (datetime.now().strftime("%H:%M:%S.%f"), s))


FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
FLANN_INDEX_LSH = 6


# 初始化
def init_feature(name):
    chunks = name.split('-')
    if chunks[0] == 'sift':  # 大图像100ms 小图像5ms
        detector = cv2.xfeatures2d.SIFT_create()
        norm = cv2.NORM_L2
    elif chunks[0] == 'surf':  # 500ms
        detector = cv2.xfeatures2d.SURF_create(800)
        norm = cv2.NORM_L2
    elif chunks[0] == 'orb':  # 500ms 算不出来
        detector = cv2.ORB_create()
        norm = cv2.NORM_HAMMING
    elif chunks[0] == 'akaze':  # 60ms 算不出来
        detector = cv2.AKAZE_create()
        norm = cv2.NORM_HAMMING
    elif chunks[0] == 'brisk':  # 100ms
        detector = cv2.BRISK_create()
        norm = cv2.NORM_HAMMING
    else:
        return None, None
    if 'flann' in chunks:
        if norm == cv2.NORM_L2:
            flann_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        else:
            flann_params = dict(algorithm=FLANN_INDEX_LSH,
                                table_number=6,  # 12
                                key_size=12,  # 20
                                multi_probe_level=1)  # 2
        matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
    else:
        matcher = cv2.BFMatcher(norm)
    return detector, matcher


# 对比并返回连线图片
def CompareTwoPictureDetail(img1, img2):
    detector, matcher = init_feature('sift')

    # 寻找特征点
    kp1, des1 = detector.detectAndCompute(img1, None)
    kp2, des2 = detector.detectAndCompute(img2, None)

    # 特征点匹配

    try:
        matches = matcher.knnMatch(des1, des2, k=2)
    except:
        matches = []

    # 筛选
    good = []
    if len(matches) > 0:
        try:
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)
        except:
            pass

    # 最少匹配10个点
    if len(good) >= MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # 寻找连线. RANSAC排除干扰
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        matchesMask = mask.ravel().tolist()

        h, w, _ = img1.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None

    draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, matchesMask=matchesMask, flags=2)
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

    return img3


# 对比两个图片
def CompareTwoPicture(pn1, pn2):
    img1 = cv2.imread(pn1, cv2.IMREAD_COLOR)
    img2 = cv2.imread(pn2, cv2.IMREAD_COLOR)
    img3 = CompareTwoPictureDetail(img1, img2)
    cv2.imshow('my img', img3)
    cv2.waitKey()
    cv2.destroyAllWindows()


# 实时对比
def RealTimeCompare(pn1):
    while True:
        img1 = cv2.imread(pn1, cv2.IMREAD_COLOR)
        img2 = WindowCaptureToMem("地下城与勇士", "地下城与勇士", 12, 549, 66, 38)
        img3 = CompareTwoPictureDetail(img1, img2)
        cv2.imshow('my img', img3)
        if (cv2.waitKey(30) & 0xFF) in [ord('q'), 27]:
            break
        time.sleep(0.3)
    cv2.destroyAllWindows()


def main():
    if len(sys.argv) < 2:
        print("usage: {} png".format(sys.argv[0]))
        exit(0)

    CompareTwoPicture(sys.argv[1], sys.argv[2])

    # RealTimeCompare(sys.argv[1])


if __name__ == "__main__":
    main()
