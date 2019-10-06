import win32gui
from screeninfo import get_monitors


def getPos():
    selectmonitor = get_monitors()[0]
    print(selectmonitor)
    width, height = 267, 150

    for i in range(selectmonitor.y, selectmonitor.y + selectmonitor.height, height):
        if i + height >= (selectmonitor.y + selectmonitor.height):
            continue

        for j in range(selectmonitor.x, selectmonitor.x + selectmonitor.width, width):
            if j + width >= (selectmonitor.x + selectmonitor.width):
                continue

            yield (j, i, width, height)


def main():
    windows = []

    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            windowtxt = win32gui.GetWindowText(hwnd)

            if "- VNC Viewer" in windowtxt:
                print(windowtxt)
                windows.append((hwnd, windowtxt))

    win32gui.EnumWindows(winEnumHandler, None)
    windows.sort(key=lambda window: window[1])
    iter = getPos()
    for (hwnd, windowtext) in windows:
        (i, j, width, height) = next(iter)
        win32gui.MoveWindow(hwnd, i, j, width, height, True)


if __name__ == '__main__':
    main()
