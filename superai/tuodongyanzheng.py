import logging
import os
import sys
from cv2 import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from superai.anjian import aj
from superai.common import InitLog, KongjianSleep
from superai.screenshots import WindowCaptureToFile
from superai.pathsetting import GetvercodeDir

logger = logging.getLogger(__name__)


def GetRightPos(image):
    # 边缘检测
    canny = cv2.Canny(image, 200, 400)

    # 轮廓提取
    img, contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rightRectangles = []
    for i, contour in enumerate(contours):
        M = cv2.moments(contour)

        if M['m00'] == 0:
            cx, cy = 0, 0
        else:
            cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']

        if 1000 < cv2.contourArea(contour) < 1300 and 120 < cv2.arcLength(contour, True) < 400:
            if cx > 100:
                x, y, w, h = cv2.boundingRect(contour)  # 外接矩形
                rightRectangles.append((x, y, w, h))

    if len(rightRectangles) > 0:
        # 内侧方块
        current = min(rightRectangles, key=lambda s: s[2] * s[3])
        x, y, w, h = current[0], current[1], current[2], current[3]
        return x, y, w, h

    return 0, 0, 0, 0


#
# for i in range(1, 11):
#     imgname = 'D:/win/reference/project/superai/superimg/tuodong%d.png' % i
#     img0 = cv2.imread(imgname, cv2.IMREAD_GRAYSCALE)
#     x, y, w, h = GetRightPos(img0)
#
#     print("x: %d y: %d w: %d h: %d 中心点: (%d, %d)" % (x, y, w, h, x + w // 2, y + h // 2))
#

def main():
    InitLog()

    gli = (31, 21, 37, 37)
    glp = (31 + 37 // 2, 21 + 37 // 2)

    print("固定左侧 x: %d y: %d w: %d h: %d 中心点: (%d, %d)" % (
        gli[0], gli[1], gli[2], gli[3], glp[0], glp[1]))

    imgfile = WindowCaptureToFile("TWINCONTROL", "WeGame", GetvercodeDir(), 284, 171, 280, 161)

    if imgfile == "":
        logger.warning("截取验证拖动图片失败")
        return

    img = cv2.imread(imgfile, cv2.IMREAD_GRAYSCALE)

    x, y, w, h = GetRightPos(img)
    grp = (x + w // 2, y + h // 2)
    print("x: %d y: %d w: %d h: %d 中心点: (%d, %d)" % (x, y, w, h, grp[0], grp[1]))

    dis = grp[0] - glp[0]
    print("横轴距离: %d" % (dis))

    beginx, beginy = 333, 354
    aj().MouseMoveToTgp(333, 354), KongjianSleep()
    aj().MouseLeftDown(), KongjianSleep()
    aj().MouseMoveR(10, 0), KongjianSleep()

    movetox, movetoy = beginx + dis, beginy
    print("移动到 %d %d" % (movetox, movetoy))
    aj().MouseMoveToTgp(movetox, movetoy)
    aj().MouseLeftUp(), KongjianSleep()


if __name__ == '__main__':
    main()
