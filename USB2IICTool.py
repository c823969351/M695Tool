from ctypes import *
import platform
from time import sleep
from usb_device import *
from usb2iic import *


class USB2IIC(object):
    def __init__(self):
        self.DevHandles = (c_uint * 20)()
        self.DevIndex = 0
        self.IICIndex = 0
        self.IICConfig = IIC_CONFIG()
        


    def Scan_device(self):
        ret = USB_ScanDevice(byref(self.DevHandles))
        if(ret == 0):
            print("No device connected!")
            return 1
        else:
            print("Have %d device connected!"%ret)

    def Open_device(self):
        ret = USB_OpenDevice(self.DevHandles[self.DevIndex])
        if(bool(ret)):
            print("Open device success!")
        else:
            print("Open device faild!")
            return 1

    def Get_device_infomation(self):
        USB2XXXInfo = DEVICE_INFO()
        USB2XXXFunctionString = (c_char * 256)()
        ret = DEV_GetDeviceInfo(self.DevHandles[self.DevIndex],byref(USB2XXXInfo),byref(USB2XXXFunctionString))
        if(bool(ret)):
            print("USB2XXX device infomation:")
            print("--Firmware Name: %s"%bytes(USB2XXXInfo.FirmwareName).decode('ascii'))
            print("--Firmware Version: v%d.%d.%d"%((USB2XXXInfo.FirmwareVersion>>24)&0xFF,(USB2XXXInfo.FirmwareVersion>>16)&0xFF,USB2XXXInfo.FirmwareVersion&0xFFFF))
            print("--Hardware Version: v%d.%d.%d"%((USB2XXXInfo.HardwareVersion>>24)&0xFF,(USB2XXXInfo.HardwareVersion>>16)&0xFF,USB2XXXInfo.HardwareVersion&0xFFFF))
            print("--Build Date: %s"%bytes(USB2XXXInfo.BuildDate).decode('ascii'))
            print("--Serial Number: ",end='')
            for i in range(0, len(USB2XXXInfo.SerialNumber)):
                print("%08X"%USB2XXXInfo.SerialNumber[i],end='')
            print("")
            print("--Function String: %s"%bytes(USB2XXXFunctionString.value).decode('ascii'))
        else:
            print("Get device infomation faild!")
            return 1
    
    def Initialize_i2c(self,clk=100000):
        self.IICConfig.ClockSpeed = clk
        self.IICConfig.Master = 1
        self.IICConfig.AddrBits = 7
        self.IICConfig.EnablePu = 1
        # 初始化IIC
        ret = IIC_Init(self.DevHandles[self.DevIndex],self.IICIndex,byref(self.IICConfig));
        if ret != IIC_SUCCESS:
            print("Initialize iic faild!")
            return 1
        else:
            print("Initialize iic sunccess!")
        
    
    def Scan_reply_device(self):
        # 扫描IIC总线上能正常应答的设备
        slavelist = ''
        SlaveAddr = (c_ushort * 128)()
        SlaveAddrNum = IIC_GetSlaveAddr(self.DevHandles[self.DevIndex],self.IICIndex,byref(SlaveAddr))
        if SlaveAddrNum <= 0:
            print("Get iic address faild!")
            return 1
        else:
            print("Get iic address sunccess!")
            print("IIC addr:")
            for i in range(0,SlaveAddrNum):
                print("%02X "%SlaveAddr[i],end='')
                slavelist = ' '.join([slavelist,hex(SlaveAddr[i])])
            print("")
            return slavelist
    
    def IIC_init(self,clk):
        ret = self.Scan_device()
        if ret == 1:
            return 1
        ret = self.Open_device()
        if ret == 1:
            return 1
        ret = self.Get_device_infomation()
        if ret == 1:
            return 1
        ret = self.Initialize_i2c(clk)
        if ret == 1:
            return 1
        ret = self.Scan_reply_device()
        if ret == 1:
            return 1
        else:
            return ret
    
    def IIC_write(self,SlaveAddr,WriteBuffer,TimeOutMs=100):
        ret = IIC_WriteBytes(self.DevHandles[self.DevIndex],self.IICIndex,SlaveAddr,byref(WriteBuffer),len(WriteBuffer),TimeOutMs)
        if ret != IIC_SUCCESS:
            print("Write iic faild!")
            return(1)
        else:
            print("Write iic sunccess!")
        sleep(0.01)
        return(0)
    
    def IIC_read(self,SlaveAddr,ReadBuffer,TimeOutMs=100):
        ret = IIC_ReadBytes(self.DevHandles[self.DevIndex],self.IICIndex,SlaveAddr,byref(ReadBuffer),len(ReadBuffer),TimeOutMs)
        if ret != IIC_SUCCESS:
            print("Write iic faild!")
            return(1)
        else:
            print("Write iic sunccess!")
            print("Read {} Slave Data:".format(hex(SlaveAddr)))
            if len(ReadBuffer) > 1:
                for i in range(0,len(ReadBuffer)):
                    print("%02X "%ReadBuffer[i],end='')
            else:
                print("%02X "%ReadBuffer[0],end='')
            print("")
        
    
    def IIC_Transfer(self,SlaveAddr,WriteBuffer,ReadBuffer,TimeOutMs=100):
        ret = IIC_WriteReadBytes(self.DevHandles[self.DevIndex],self.IICIndex,SlaveAddr,byref(WriteBuffer),len(WriteBuffer),byref(ReadBuffer),len(ReadBuffer),TimeOutMs)
        if ret != IIC_SUCCESS:
            print("WriteRead iic faild!")
            return 1
        else:
            print("WriteRead iic sunccess!")
            # print("Read %02X Data:",WriteBuffer[0])
            print("Read {} Data:".format(hex(WriteBuffer[0])))
            if len(ReadBuffer) > 1:
                for i in range(0,len(ReadBuffer)):
                    print("%02X "%ReadBuffer[i],end='')
            else:
                print("%02X "%ReadBuffer[0],end='')
            print("")
            return 0
    
    def Close_device(self):
        # Close device
        ret = USB_CloseDevice(self.DevHandles[self.DevIndex])
        if(bool(ret)):
            print("Close device success!")
        else:
            print("Close device faild!")
            exit()
    
    def power_read(self,SlaveAddr,Regaddr,TimeOutMs=100):
        WriteBuffer = (c_uint8 * 1)(Regaddr)
        ReadBuffer = (c_uint8 * 2)()
        self.IIC_Transfer(SlaveAddr,WriteBuffer,ReadBuffer)
        value = hex(ReadBuffer[0]).split('x')[1] + hex(ReadBuffer[1]).split('x')[1]
        return int(value,16)
    
    def data_read(self,SlaveAddr,Regaddr,WriteLen = 1,ReadLen = 2,TimeOutMs=100):
        WriteBuffer = (c_uint8 * WriteLen)(Regaddr)
        ReadBuffer = (c_uint8 * ReadLen)()
        value = ''
        self.IIC_Transfer(SlaveAddr,WriteBuffer,ReadBuffer)
        for i in range(ReadLen):
            value += hex(ReadBuffer[i]) + ' '
        return value
    
    def data_write(self,SlaveAddr,Regaddr,WriteLen = 1,ReadLen = 0,TimeOutMs=100):
        pass
    


if __name__ == '__main__': 
    dev = USB2IIC()
    dev.IIC_init(1000000)
    SlaveAddr = 0x4C
    a = dev.volt_read(SlaveAddr)
    print(a)
    # dev.IIC_read(SlaveAddr,ReadBuffer)
    dev.Close_device()