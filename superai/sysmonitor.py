import wmi
import platform


# 操作系统
def sysVersion():
    c = wmi.WMI()
    sysinfo = c.Win32_OperatingSystem()
    if len(sysinfo) < 1:
        raise NotImplementedError("取操作系统信息错误")
    sysinfo = sysinfo[0]
    return "Version: %s %s %s" % (sysinfo.Caption, sysinfo.OSArchitecture, sysinfo.BuildNumber)

# 磁盘
def diskInfo():
    c = wmi.WMI()
    # 设备名称
    for physical_disk in c.Win32_DiskDrive():

        # 序列号
        print(physical_disk.SerialNumber)

        for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                print(physical_disk.Caption, partition.Caption, logical_disk.Caption)

    # 磁盘信息
    for disk in c.Win32_LogicalDisk(DriveType=3):
        print(disk.Caption, "%0.2f%% free" % (100.0 * int(disk.FreeSpace) / int(disk.Size)))



def main():
    print(sysVersion())

    diskInfo()


if __name__ == '__main__':
    main()
