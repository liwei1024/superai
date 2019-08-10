import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

from ctypes import *
from superai.defer import defer

import cv2

from superai.screenshots import WindowCaptureToMem

winGPUdll = "E:/win/reference/refer/darknet/build/darknet/x64/yolo_cpp_dll.dll"
lib = CDLL(winGPUdll, RTLD_GLOBAL)

lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]


class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]


class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


# cfg, weight
load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

# data
load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

# 加载图片
load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

# 释放图片
free_image = lib.free_image
free_image.argtypes = [IMAGE]

# 预测图片
predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

# 获取窗口?
get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

# 排序?
do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

# 释放寻找点
free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

altNames = None


def array_to_image(arr):
    import numpy as np
    # need to return old values to avoid python freeing memory
    arr = arr.transpose(2, 0, 1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
    data = arr.ctypes.data_as(POINTER(c_float))
    im = IMAGE(w, h, c, data)
    return im, arr


def detectImageShots(net, meta, thresh=.5, hier_thresh=.5, nms=.45, debug=False):
    customImageBGR = WindowCaptureToMem("地下城与勇士", "地下城与勇士")
    customImage = cv2.cvtColor(customImageBGR, cv2.COLOR_BGR2RGB)
    # customImage = cv2.resize(customImage, (lib.network_width(net), lib.network_height(net)),
    #                          interpolation=cv2.INTER_LINEAR)

    image, arr = array_to_image(customImage)

    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, image)
    dets = get_network_boxes(net, customImageBGR.shape[1], customImageBGR.shape[0], thresh, hier_thresh, None, 0,
                             pnum, 0)
    defer(lambda: (free_detections(dets, num)))

    num = pnum[0]
    if nms:
        do_nms_sort(dets, num, meta.classes, nms)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                nameTag = meta.names[i] if altNames is None else altNames[i]
                res.append((nameTag, dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    return customImageBGR, res


@defer
def detectImageFile(net, meta, imageFile, thresh=.5, hier_thresh=.5, nms=.45, debug=False, defer=None):
    image = load_image(imageFile, 0, 0)
    defer(lambda: (free_image(image)))

    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, image)
    dets = get_network_boxes(net, image.w, image.h, thresh, hier_thresh, None, 0, pnum, 0)
    defer(lambda: (free_detections(dets, num)))

    num = pnum[0]
    if nms:
        do_nms_sort(dets, num, meta.classes, nms)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                nameTag = meta.names[i] if altNames is None else altNames[i]
                res.append((nameTag, dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    return res


def main():
    configPath = "E:/win/reference/project/yolotest/cfg/dnf-yolov3-voc.cfg"
    weightPath = "E:/win/reference/project/yolotest/backup/dnf-yolov3-voc_1000.weights"
    metaPath = "E:/win/reference/project/yolotest/cfg/dnf-obj.data"

    global altNames

    # 读取 cfg, weight
    net = load_net_custom(configPath.encode("ascii"), weightPath.encode("ascii"), 0, 1)

    # 读取 data
    meta = load_meta(metaPath.encode("ascii"))

    # 读取 data (图片列表, names, backup)  => 获取names
    altNames = getNames(metaPath)

    thresh = 0.25

    # 测试指定图片
    # imageFile = "E:/win/studio/dxf/picture/tmp/0001.jpg"
    # detections = detectImageFile(net, meta, imageFile.encode("ascii"), thresh)
    # print(detections)

    # 截图

    while True:
        customImage, detections = detectImageShots(net, meta, thresh)
        print(detections)

        for i in range(len(detections)):
            bounds = detections[i][2]
            w = int(bounds[2])
            h = int(bounds[3])
            xCoord = int(bounds[0] - bounds[2] / 2)
            yCoord = int(bounds[1] - bounds[3] / 2)
            pt1 = (xCoord, yCoord)
            pt2 = (xCoord + w, yCoord + h)
            customImage = cv2.rectangle(customImage, pt1, pt2, 4)

        cv2.imshow('my img', customImage)

        if (cv2.waitKey(200) & 0xFF) in [ord('q'), 27]:
            break

    cv2.destroyAllWindows()


def getNames(metaPath: str) -> [str]:
    altNames = None
    with open(metaPath) as fmeta:
        metaContents = fmeta.read()
        import re
        match = re.search("names *= *(.*)$", metaContents, re.IGNORECASE | re.MULTILINE)
        result = match.group(1)
        if os.path.exists(result):
            with open(result) as fnames:
                namesList = fnames.read().strip().split("\n")
                altNames = [x.strip() for x in namesList]
    return altNames


if __name__ == "__main__":
    main()
