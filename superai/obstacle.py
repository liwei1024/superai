from superai.gameapi import GameApiInit


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)


if __name__ == "__main__":
    main()
