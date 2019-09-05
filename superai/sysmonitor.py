import sys
sys.coinit_flags = 0
import pythoncom
import wmi
import platform
import psutil


# 操作系统
def sysVersion():
    pythoncom.CoInitialize()

    c = wmi.WMI()

    obj = c.Win32_OperatingSystem()
    if len(obj) < 1:
        raise NotImplementedError("取操作系统信息错误")
    obj = obj[0]

    result = {
        "version": obj.Caption,
        "osarch": obj.OSArchitecture,
        "build number": obj.BuildNumber,
    }


    pythoncom.CoUninitialize()
    return result


# cpu
def cpuInfo():
    pythoncom.CoInitialize()

    c = wmi.WMI()
    obj = c.Win32_Processor()
    if len(obj) < 1:
        raise NotImplementedError("取cpu信息错误")
    obj = obj[0]

    result = {
        "cpuname": obj.Name.strip(),
        "usage": psutil.cpu_percent(interval=None),
    }

    pythoncom.CoUninitialize()

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
    pythoncom.CoInitialize()

    c = wmi.WMI()
    obj = c.Win32_DiskDrive()
    if len(obj) < 1:
        raise NotImplementedError("读取磁盘信息错误")

    obj = obj[0]
    obj2 = psutil.disk_usage('/')

    result = {
        "serialnumber": obj.SerialNumber,
        "used": obj2.used,
        "total": obj2.total
    }

    pythoncom.CoUninitialize()

    return result


# 网卡/ip信息
def networkInfo():
    obj = psutil.net_if_addrs()
    result = {}
    for key, v in obj.items():
        if "WLAN" in key:
            result[key] = {
                "ip": v[1].address,
                "mac": v[0].address
            }

    return result


def main():
    print("system: " + str(sysVersion()))
    # print("cpu: " + str(cpuInfo()))
    # print("mem: " + str(memInfo()))
    # print("disk: " + str(diskInfo()))
    # print("net: " + str(networkInfo()))


if __name__ == '__main__':
    main()
