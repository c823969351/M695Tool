# -*- coding: utf-8 -*-

__author__ = 'chenjiwen'


#导入程序运行必须模块

from fileinput import filename
from logging import exception
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

REG_VOLT = 0x02
REG_CURRENT= 0x04
enable = 0
volt = 0
current = 0
num = 0

CLK_LIST = ['100k','200k','400k']

def clk_2_number(index):
    number = {
        0 : 100000,
        1 : 200000,
        2 : 400000
    }
    return number.get(index,None)

def volt_value_conv(value):
    global volt
    volt = value * 0.00125
    return value * 0.00125

def current_value_conv(value):
    global current
    global num
    current = value * num
    return value * num

class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):

        super(MyMainForm, self).__init__(parent)

        self.setupUi(self)
        self.comboBox_CLK.addItems(CLK_LIST)
        self.IIC= USB2IIC()
        self.pushButton_init.clicked.connect(self.dev_init)
        self.pushButtonStart.clicked.connect(self.work)
        self.pushButtonStop.clicked.connect(self.stop)
        self.workThread = My_thread()
        self.workThread.show.connect(self.show_power)
    
    def dev_init(self):
        try:
            clk = self.comboBox_CLK.currentIndex()
            clk = clk_2_number(clk)
            ret = self.IIC.IIC_init(clk)
            if ret == 1:
                self.message_warning()
            else:
                self.message_done(ret)
        except Exception as e:
            print(e)
    
    def IIC_config(self):
        try:
            self.iicaddr = int(self.lineEdit_IICAddr.text(),16)
            reg_00 = int(self.lineEdit_00H.text(),16)
            reg_05 = int(self.lineEdit_05H.text(),16)
            WriteBuffer = (c_uint16 * 2)(reg_00,reg_05)
            print(WriteBuffer[0],WriteBuffer[1])
            ret = self.IIC.IIC_write(self.iicaddr,WriteBuffer)
            if ret == 1:
                self.message_warning()
            else:
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
        global num
        num = float(self.lineEdit_currentlsb.text())
        # self.IIC_config()
        # WriteBuffer = (c_uint8 * 1)(REG_VOLT)
        # ReadBuffer_volt = (c_uint16 * 1)()
        # self.IIC.IIC_Transfer(self.iicaddr,WriteBuffer,ReadBuffer_volt)
        # WriteBuffer = (c_uint8 * 1)(REG_CURRENT)
        # ReadBuffer_curr = (c_uint16 * 1)()
        # self.IIC.IIC_Transfer(self.iicaddr,WriteBuffer,ReadBuffer_curr)
        self.workThread.start()

    def stop(self):
        num = float(self.lineEdit_currentlsb.text())
        print(num)

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
        print(1111111111)
        ReadBuffer_volt = (c_uint16 * 1)(2167)
        ReadBuffer_curr = (c_uint16 * 1)(3200)
        for i in range(10):
            volt = volt_value_conv(ReadBuffer_volt[0])
            current = current_value_conv(ReadBuffer_curr[0])
            self.show.emit()    
            ReadBuffer_volt[0] += 1000
            ReadBuffer_curr[0] += 1000
            time.sleep(0.1)
 
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