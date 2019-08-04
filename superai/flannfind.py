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

    # 寻找特征点 / 描述
    kp1, des1 = detector.detectAndCompute(img1, None)
    kp2, des2 = detector.detectAndCompute(img2, None)

    # 特征点匹配
    try:
        matches = matcher.knnMatch(des1, des2, k=2)
    except:
        matches = []

    # m:最近距离 / n:次近距离 < 0.7 阀值
    good = []
    if len(matches) > 0:
        try:
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)
        except:
            pass

    if len(good) >= MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        # 画方框
        h, w, _ = img1.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None

    # 画线
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


# 全局 detector, matcher
# gDetector, gMatcher = init_feature('sift')

class Picture:
    def __init__(self, picturefile, dx=0, dy=0, dw=0, dh=0):
        self.picturefile = picturefile
        self.dx = dx
        self.dy = dy
        self.dw = dw
        self.dh = dh

        self.img1 = cv2.imread(self.picturefile, cv2.IMREAD_COLOR)

    def Match(self):
        self.img2 = WindowCaptureToMem("地下城与勇士", "地下城与勇士", self.dx, self.dy, self.dw, self.dh)
        return FindPicture(self.img1, self.img2)

    def Pos(self):
        self.img2 = WindowCaptureToMem("地下城与勇士", "地下城与勇士")
        return FindPicturePos(self.img1, self.img2)


def sifttest():
    if len(sys.argv) < 2:
        print("usage: {} png".format(sys.argv[0]))
        exit(0)
    CompareTwoPicture(sys.argv[1], sys.argv[2])
    # RealTimeCompare(sys.argv[1])


def templatefindtest():
    if len(sys.argv) < 2:
        print("usage: {} png".format(sys.argv[0]))
        exit(0)

    img1 = cv2.imread(sys.argv[1], cv2.IMREAD_COLOR)
    img2 = cv2.imread(sys.argv[2], cv2.IMREAD_COLOR)
    FindPictureTest(img1, img2)


# 寻找图片
def FindPictureTest(img1, img2):
    t1 = time.time()
    h, w = img1.shape[:2]
    res = cv2.matchTemplate(img2, img1, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img2, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        print(pt[0] + w / 2.0, pt[1] + h / 2.0)

    t2 = time.time()
    print(t2 - t1)
    cv2.imshow('my img', img2)
    cv2.waitKey()
    cv2.destroyAllWindows()


# img1是否在img2上出现过
def FindPicture(img1, img2):
    res = cv2.matchTemplate(img2, img1, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    flag = False
    for _ in zip(*loc[::-1]):
        flag = True
    return flag


# img1在img2上的相对pos
def FindPicturePos(img1, img2):
    h, w = img1.shape[:2]
    res = cv2.matchTemplate(img2, img1, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        return pt[0] + w / 2.0, pt[1] + h / 2.0
    return 0, 0


if os.path.exists("c:/win/superimg/"):
    basedir = "c:/win/superimg/"
elif os.path.exists("D:/win/superimg/"):
    basedir = "D:/win/superimg/"
else:
    basedir = "D:/win/studio/dxf/picture/superimg/"

cartoonScene = Picture(basedir + "/cartoon-scene.png", 12, 549, 66, 38)
videoScene = Picture(basedir + "/video-scene.png", 663, 554, 121, 18)
confirm = Picture(basedir + "/confirm.png", 245, 126, 324, 378)

gCartoonTop = False
gVideoTop = False
gConfirmTop = False

gFlushExit = False


# 是否有动画置顶 (背景线程刷新)
def IsCartoonTop():
    return gCartoonTop


# 是否有视频置顶 (背景线程刷新)
def IsVideoTop():
    return gVideoTop


# 是否有确认键置顶 (背景线程刷新)
def IsConfirmTop():
    return gConfirmTop


# 获取确认键位置
def GetConfirmPos():
    return confirm.Pos()


# 设置截屏线程退出
def SetThreadExit():
    global gFlushExit
    gFlushExit = True


# 不断截图把图片状态置到内存中
def FlushImg():
    global gCartoonTop
    global gVideoTop
    global gConfirmTop
    global gFlushExit

    try:
        while not gFlushExit:
            # 是否有动画
            if cartoonScene.Match():
                gCartoonTop = True
            else:
                gCartoonTop = False

            # 是否有视频
            if videoScene.Match():
                gVideoTop = True
            else:
                gVideoTop = False

            # 是否有确认按钮
            if confirm.Match():
                gConfirmTop = True
            else:
                gConfirmTop = False

            time.sleep(0.3)

    except Exception as e:
        Log("flushimg thread error " + e)
        sys.exit()


def main():
    # while True:
    #     if IsCartoonTop():
    #         Log("1")
    #     time.sleep(0.5)

    # sifttest()

    templatefindtest()
    pass


if __name__ == "__main__":
    main()
