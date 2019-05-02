import cv2
from matplotlib import pyplot as plt


def main():
    man = cv2.imread("E:/win/tmp/capture/man.bmp")
    map1_1 = cv2.imread("E:/win/tmp/capture/map_1.bmp")

    orb = cv2.ORB_create()

    kp1, des1 = orb.detectAndCompute(man, None)
    kp2, des2 = orb.detectAndCompute(map1_1, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    matches = sorted(matches, key=lambda x: x.distance)

    resultImg = cv2.drawMatches(man, kp1, map1_1, kp2, matches[:25], map1_1, flags=2)

    plt.imshow(resultImg), plt.show()


if __name__ == "__main__":
    main()
