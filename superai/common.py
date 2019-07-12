from datetime import datetime


def Log(s):
    print("%s %s" % (datetime.now().strftime("%H:%M:%S.%f"), s))