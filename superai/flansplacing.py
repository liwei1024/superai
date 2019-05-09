import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import numpy as np

import threading


from superai.screenshots import WindowCaptureToMem
import cv2

MIN_MATCH_COUNT = 10

TEST = False


def main():
    global TEST

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            TEST = True

    imgAlready = None

    while True:
        if imgAlready is None:
            a = input("初始图片,press any key\n")
            img1 = WindowCaptureToMem("地下城与勇士", "地下城与勇士")
        else:
            img1 = imgAlready

        b = input("p=拼接图片, s=存储图片\n")
        if b.lower() == 's':
            # TODO 小地图矩形判断场景数 + 位置 + 当前是第几个图
            a = input("input sceneidx x y\n")
            num, x, y = [t(s) for t, s in zip((int, int, int), a.split())]
            saveImgName = "E:/win/studio/dxf/picture/001_005_yaml/sceneA_{}_{}_{}.png".format(num, x, y)
            cv2.imwrite(saveImgName, imgAlready, [int(cv2.IMWRITE_PNG_COMPRESSION)])
            print("图片: {} 存储成功".format(saveImgName))
            imgAlready = None
            continue

        img2 = WindowCaptureToMem("地下城与勇士", "地下城与勇士")

        # img1 = cv2.imread("E:/win/tmp/capture/1.bmp")
        # img2 = cv2.imread("E:/win/tmp/capture/2.bmp")

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
            img2_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            # dst 特征点
            img1_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)

            # img2 相对于 img1的 变换, 计算出关键点的变换
            M, mask = cv2.findHomography(img2_pts, img1_pts, cv2.RANSAC, 5.0)

            print("变换矩阵:\n {}".format(M))

            # M -> 图片一转换到图片二的坐标系经过的矩阵变换?
            # [[9.99757567e-01 - 1.41728525e-05 - 5.43868856e+02]
            #  [-1.72527468e-04  9.99741953e-01  9.09084640e-02]
            # [-4.40879493e-07 - 2.57468938e-08  1.00000000e+00]]

            # 特征点匹配的掩码?
            matchesMask = mask.ravel().tolist()

            if not TEST:
                h, w, _ = img2.shape
                rect2 = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)  # 行数未知, 1列, 2个维度
                print("矩形2: {}".format(rect2))
                rect2 = cv2.perspectiveTransform(rect2, M)

                print("矩形2(变换后): {}".format([np.int32(rect2)]))
                # newimg = cv2.polylines(img1, [np.int32(rect2)], True, [51, 153, 255], 1, cv2.LINE_8)

                xxx = [np.int32(rect2)]
                neww = xxx[0][2][0][0]
                newh = xxx[0][2][0][1]
                print("右图变换到左图的坐标系后的, 图片尺寸w={},h={}".format(neww, newh))

                newimg = cv2.warpPerspective(img2, M, (neww, newh))

                img1h, img1w, _ = img1.shape
                newimgh, newimgw, _ = newimg.shape

                tranminw = min(img1w, newimgw)
                tranminh = min(img1h, newimgh)

                newimg[0:tranminh, 0:tranminw] = img1[0:tranminh, 0:tranminw]

                imgAlready = newimg

                # cv2.imshow('my img', newimg)
                # cv2.waitKey()
                # cv2.destroyAllWindows()

                continue
            else:
                # 画方框
                h, w, _ = img2.shape
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                img1 = cv2.polylines(img1, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

        else:
            print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
            matchesMask = None

        # 显示两个图的相似点的连线

        # matchColor=(0, 255, 0),
        #  matchesMask=matchesMask,
        draw_params = dict(singlePointColor=None,
                           matchesMask=None,
                           flags=2)

        img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

        cv2.imshow('my img', img3)
        cv2.waitKey()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
