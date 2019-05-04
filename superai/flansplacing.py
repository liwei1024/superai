import sys
import os
import time

import numpy as np

from matplotlib import pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import cv2

MIN_MATCH_COUNT = 10


def main():
    img1 = cv2.imread("E:/win/tmp/capture/1.bmp")
    img2 = cv2.imread("E:/win/tmp/capture/2.bmp")

    # 创建sift检测器
    sift = cv2.xfeatures2d.SIFT_create()

    # 关键点 , 描述符
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # 匹配特征点
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # 筛选较好的特征对
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        # src 特征点
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)

        # dst 特征点
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # 计算出关键点的变换
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        print("变换矩阵:\n {}".format(M))

        # M -> 图片一转换到图片二的坐标系经过的矩阵变换?
        # [[9.99757567e-01 - 1.41728525e-05 - 5.43868856e+02]
        #  [-1.72527468e-04  9.99741953e-01  9.09084640e-02]
        # [-4.40879493e-07 - 2.57468938e-08  1.00000000e+00]]

        # 特征点匹配的掩码?
        matchesMask = mask.ravel().tolist()

        # <class 'numpy.ndarray'>
        # print(type(dst_pts))

        newimg = cv2.warpPerspective(img2, M, (800, 600))

        cv2.imshow('my img', newimg)
        cv2.waitKey()
        cv2.destroyAllWindows()

        exit(0)

        # h, w = img1.shape
        # pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # 透视变换
        # dst = cv2.perspectiveTransform(pts, M)
        # img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None

    # 显示两个图的相似点的连线

    # matchColor=(0, 255, 0),
    draw_params = dict(singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)

    img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

    cv2.imshow('my img', img3)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
