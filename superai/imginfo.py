import cv2

ImgName = "E:/win/tmp/capture/1.bmp"


def main():
    img = cv2.imread(ImgName)
    w, h, channelN = img.shape
    print("w: {} h: {} channel: {}".format(w, h, channelN))
    print("size: {}".format(img.size))
    print("datatype: {}".format(img.dtype))

    cv2.imshow('my img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
