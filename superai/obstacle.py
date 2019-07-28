import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))


from superai.gameapi import GameApiInit, GetSeceneInfo, FlushPid


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)
    FlushPid()

    dixinglst, dixingvec, obstacles, wh = GetSeceneInfo()

    print("宽高: %s" % wh)


if __name__ == "__main__":
    main()
