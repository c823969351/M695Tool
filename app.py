# -*- coding: utf-8 -*-

__author__ = 'chenjiwen'


#导入程序运行必须模块

import sys
from telnetlib import PRAGMA_HEARTBEAT
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
import os
import time
#PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中

from PyQt5.QtWidgets import *

#导入designer工具生成的login模块

from mainwindow import Ui_MainWindow

from PyQt5.QtCore import QThread, pyqtSignal,pyqtSlot,QWaitCondition,QMutex

#导入设备库
from USB2IICTool import USB2IIC
from ctypes import *
from zhexiantu import *
from write_excel import *

REG_VOLT = 0x02
REG_CURRENT= 0x04
enable = 0
volt = 0
current = 0
currenlsb = 1
voltATT= 1
file_name = ''
IICaddr=0
time_interval = 0.1

CLK_LIST = ['100k','200k','400k']

IIC= USB2IIC()

def time_monitor():
    print('************')
    nowtime = time.localtime()
    strftime_1 = time.strftime("%Y%m%d-%H-%M-%S", nowtime)
    file_1 = os.getcwd()
    name = file_1+'\\测试数据\\电源测试{}.csv'.format(strftime_1)
    global file_name
    file_name = name
    print(file_name)

def csv_reader():
        df = line_chart(file_name)
        df.drew()

def clk_2_number(index):
    number = {
        0 : 100000,
        1 : 200000,
        2 : 400000
    }
    return number.get(index,None)

def volt_value_conv(value):
    global volt
    volt = value * 0.00125 * voltATT
    return volt

def current_value_conv(value):
    global current
    global currenlsb
    current = value * currenlsb
    return current

class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):

        super(MyMainForm, self).__init__(parent)

        self.setupUi(self)
        self.comboBox_CLK.addItems(CLK_LIST)
        self.pushButton_init.clicked.connect(self.dev_init)
        self.pushButtonStart.clicked.connect(self.work)
        self.pushButtonStop.clicked.connect(self.stop_thread)
        self.pushButton_readdata.clicked.connect(self.read_data)
        self.pushButton_writedata.clicked.connect(self.write_data)
        self.pushButton_openfile.clicked.connect(self.open_file)
    
    def open_file(self):
        try:
            os.startfile('测试数据')
        except Exception as e:
            print(e)

    def dev_init(self):
        try:
            clk = self.comboBox_CLK.currentIndex()
            clk = clk_2_number(clk)
            ret = IIC.IIC_init(clk)
            if ret == 1:
                self.message_warning()
            else:
                self.message_done(ret)
        except Exception as e:
            print(e)
    
    def IIC_config(self):
        try:
            global IICaddr
            self.iicaddr = int(self.lineEdit_IICAddr.text(),16)

            data = self.lineEdit_00H.text().split(' ')
            for i in range(len(data)):
                data[i] = int(data[i],16)
            WriteBuffer_reg00 = (c_uint8 * 3)(0x00,data[0],data[1])
            print(WriteBuffer_reg00[0],WriteBuffer_reg00[1],WriteBuffer_reg00[2])
            ret = IIC.IIC_write(self.iicaddr,WriteBuffer_reg00)
            if ret == 1:
                self.message_warning()
            else:
                IICaddr = self.iicaddr
                pass

            data = self.lineEdit_05H.text().split(' ')
            for i in range(len(data)):
                data[i] = int(data[i],16)
            WriteBuffer_reg05 = (c_uint8 * 3)(0x05,data[0],data[1])
            print(WriteBuffer_reg05[0],WriteBuffer_reg05[1],WriteBuffer_reg05[2])
            ret = IIC.IIC_write(self.iicaddr,WriteBuffer_reg05)
            if ret == 1:
                self.message_warning()
            else:
                IICaddr = self.iicaddr
                pass
            
        except Exception as e:
            print(e)
    
    def show_power(self):
        try:
            global volt
            global current
            print(volt,current)
            self.lcdNumberVolt.display(volt)
            self.lcdNumberCurrent.display(current)
        except Exception as e:
            print(e)
    
    def work(self):
        try:
            global currenlsb
            global voltATT
            global time_interval
            if self.lineEdit_currentlsb.text():
                currenlsb = float(self.lineEdit_currentlsb.text())
            else:
                currenlsb = 1
            if self.lineEdit_VoltATT.text():
                voltATT = float(self.lineEdit_VoltATT.text())
            else:
                voltATT = 1
            time_interval = (int(self.spinBoxTimeRead.value()) * 0.001) 
            self.IIC_config()
            self.workThread = My_thread()
            self.workThread.show.connect(self.show_power)
            self.workThread.start()
        except Exception as e:
            print(e)

    def stop_thread(self):
        try:
            if self.workThread:
                self.workThread.terminate()
                self.workThread = None
                # self.msg_dialog.close()     # 停止线程时，关闭弹窗
                # csv_reader()
            else:
                self.message_warning()
            
            self.lcdNumberVolt.display(0)
            self.lcdNumberCurrent.display(0)
        except Exception as e:
            print(e)
            self.message_warning()
    
    def read_data(self):
        try:
            slaveaddr = int(self.lineEdit_slaveaddr.text(),16)
            if self.lineEdit_regaddr.text():
                regaddr = int(self.lineEdit_regaddr.text(),16)
            else:
                regaddr = 0x00
            bytelen = int(self.spinBox_bytenum.value())
            data = IIC.data_read(slaveaddr,regaddr,1,bytelen)
            msg = 'R 【{:X}】[{:X}] :{}'.format(slaveaddr,regaddr,data)
            self.textBrowser.append(msg)     
        except Exception as e:
            print(e)

    def write_data(self):
        try:
            slaveaddr = int(self.lineEdit_slaveaddr.text(),16)
            if self.lineEdit_regaddr.text():
                regaddr = int(self.lineEdit_regaddr.text(),16)
            else:
                regaddr = 0x00
            data = self.lineEdit_writedata.text().split(' ')
            msg = 'W 【{:X}】[{:X}] :{}'.format(slaveaddr,regaddr,data)
            self.textBrowser.append(msg) 
            for i in range(len(data)):
                data[i] = int(data[i],16)
            print(data)
            WriteBuffer = (c_uint8*(len(data) + 1))(regaddr)
            ret = IIC.IIC_write(slaveaddr,WriteBuffer)
            if ret == 1:
                self.message_warning()
            else:
                pass
        except Exception as e:
            print(e)        

    def message_warning(self):
     #提示
     msg_box = QMessageBox(QMessageBox.Warning, '警告', '系统异常')
     msg_box.exec_()

    def message_done(self,msg):
     #提示
     msg_box = QMessageBox(QMessageBox.Information, '提示', msg)
     msg_box.exec_()



    def close(self):
        sys.exit(app.exec_())

class My_thread(QThread):
    show = pyqtSignal()
    def __init__(self):
        super(My_thread, self).__init__()
        '''
        QWaitCondition()用于多线程同步，一个线程调用QWaitCondition.wait()阻塞等待，
        直到另外一个线程调用QWaitCondition.wake()唤醒才继续往下执行
        QMutex()：是锁对象
        '''
        self._isPause = False
        self.cond = QWaitCondition()
        self.mutex = QMutex()
 
    def run(self):
        # while True:
        #     self.mutex.lock()       # 上锁
        #     if self._isPause:
        #         self.cond.wait(self.mutex)
        #     self.num_trig.emit(f'item{a}')
        #     a += 1
        #     QThread.sleep(2)
        #     self.mutex.unlock()  # 解锁
        global volt
        global current
        global file_name
        global IICaddr
        time_monitor()
        excel_creart(file_name)
        while 1:
            try:
                self.mutex.lock()       # 上锁
                value_volt = IIC.power_read(IICaddr,REG_VOLT)
                value_current = IIC.power_read(IICaddr,REG_CURRENT)              
                volt = volt_value_conv(value_volt)
                current = current_value_conv(value_current)
                self.show.emit() 
                excel_write(volt,current,file_name)
                time.sleep(time_interval)
                self.mutex.unlock()     # 解锁
            except Exception as e:
                print(e)
        # ReadBuffer_volt = (c_uint16 * 1)(2167)
        # ReadBuffer_curr = (c_uint16 * 1)(3200)
        # for i in range(10):
        #     self.mutex.lock()  
        #     volt = volt_value_conv(ReadBuffer_volt[0])
        #     current = current_value_conv(ReadBuffer_curr[0])
        #     self.show.emit()    
        #     ReadBuffer_volt[0] += 1000
        #     ReadBuffer_curr[0] += 1000
        #     excel_write(volt,current,file_name)
        #     time.sleep(0.1)
        #     self.mutex.unlock()
 
    # 线程暂停
    def pause(self):
        self._isPause = True
 
    # 线程恢复
    def resume(self):
        self._isPause = False
        self.cond.wakeAll()


if __name__ == "__main__":

    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行

    app = QApplication(sys.argv)

    #初始化

    myWin = MyMainForm()

    #将窗口控件显示在屏幕上

    myWin.show()

    #程序运行，sys.exit方法确保程序完整退出。

    sys.exit(app.exec_())