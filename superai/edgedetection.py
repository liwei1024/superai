import cv2

ImgName = "E:/win/tmp/capture/1.bmp"
CannyImgName = "E:/win/tmp/capture/1_canny.bmp"


def main():
    img = cv2.imread(ImgName)
    w, h, channelN = img.shape

    cv2.imwrite(CannyImgName, cv2.Canny(img, w, h))
    cv2.imshow("1_canny", cv2.imread(CannyImgName))
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
