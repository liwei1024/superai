import cv2



def main():
    img = cv2.imread("E:/win/tmp/capture/map_1.bmp")

    w, h, channelN = img.shape
    print("w: {} h: {} channel: {}".format(w, h, channelN))
    print("size: {}".format(img.size))
    print("datatype: {}".format(img.dtype))

    # plt.imshow(img)
    # plt.show()

    cv2.imshow('my img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
