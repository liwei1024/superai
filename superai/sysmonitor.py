import platform
import time

import psutil

gsysversionresult = None
gcpuresult = None
gmemresult = None
gdiskresult = None
gnetworkresult = None

latest_sent = None
latest_recv = None

s_is_running = True

gsleepTime = 2


def getSysversionResult():
    return sysVersion() if gsysversionresult is None else gsysversionresult


def getCpuResult():
    return cpuInfo() if gcpuresult is None else gcpuresult


def getMemResult():
    return memInfo() if gmemresult is None else gmemresult


def getDiskResult():
    return diskInfo() if gdiskresult is None else gdiskresult


def getNetworkResult():
    return networkInfo() if gnetworkresult is None else gnetworkresult


def sysFlushThread():
    while s_is_running:
        global gsysversionresult, gcpuresult, gmemresult, gdiskresult, gnetworkresult
        gsysversionresult = sysVersion()
        gcpuresult = cpuInfo()
        gmemresult = memInfo()
        gdiskresult = diskInfo()
        gnetworkresult = networkInfo()
        time.sleep(gsleepTime)


def cpuFlushStop():
    global s_is_running
    s_is_running = False


# 操作系统
def sysVersion():
    result = {
        "version": platform.version(),
        "osarch": platform.machine(),
    }
    return result


# cpu
def cpuInfo():
    result = {
        "usage": psutil.cpu_percent(interval=None),
    }
    return result


# memory
def memInfo():
    obj = psutil.virtual_memory()

    result = {
        "used": obj.used,
        "total": obj.total,
    }

    return result


# 磁盘
def diskInfo():
    obj = psutil.disk_usage('/')
    result = {

        "used": obj.used,
        "total": obj.total
    }
    return result


# 网卡/ip信息
def networkInfo():
    matchlist = ["WLAN"]

    def isInMatchList(s):
        for v in matchlist:
            if v in s:
                return True
        return False

    obj = psutil.net_if_addrs()
    result = {}
    for key, v in obj.items():
        if isInMatchList(key):
            result["result"] = {
                "ip": v[1].address,
                "mac": v[0].address
            }
            break

    obj = psutil.net_io_counters(pernic=True)
    for key, v in obj.items():
        if isInMatchList(key):
            global latest_sent, latest_recv

            if latest_sent is None and latest_recv is None:
                latest_sent, latest_recv = v.bytes_sent, v.bytes_recv
                result["result"]["persec_sent"] = 0
                result["result"]["persec_recv"] = 0
                break
            else:
                persec_sent = (v.bytes_sent - latest_sent) / gsleepTime
                persec_recv = (v.bytes_recv - latest_recv) / gsleepTime
                result["result"]["persec_sent"] = persec_sent
                result["result"]["persec_recv"] = persec_recv
                latest_sent, latest_recv = v.bytes_sent, v.bytes_recv
                break
    return result


def main():
    t1 = time.time()
    print("system: " + str(sysVersion()))
    print("cpu: " + str(cpuInfo()))
    print("mem: " + str(memInfo()))
    print("disk: " + str(diskInfo()))
    print("net: " + str(networkInfo()))
    t2 = time.time()
    print(t2 - t1)


if __name__ == '__main__':
    main()
