import os
import sys


def main():
    runPath = os.path.split(sys.executable)[0]
    globalPath = os.path.split(runPath)[0]

    print(runPath, globalPath)


if __name__ == '__main__':
    main()
