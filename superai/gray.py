import cv2

ImgName = "E:/win/tmp/capture/1.bmp"
GrayImgName = "E:/win/tmp/capture/1_gray.bmp"


def main():
    grayImage = cv2.imread(ImgName, cv2.IMREAD_GRAYSCALE)
    cv2.imwrite(GrayImgName, grayImage)


if __name__ == "__main__":
    main()
