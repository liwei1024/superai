from datetime import datetime


def Log(s):

    try:
        print("%s %s" % (datetime.now().strftime("%H:%M:%S.%f"), s))
    except UnicodeEncodeError:
        print("%s %s" % (datetime.now().strftime("%H:%M:%S.%f"), "发生了format异常"))