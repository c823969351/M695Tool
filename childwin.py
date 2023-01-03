#导入程序运行必须模块

import sys
from telnetlib import PRAGMA_HEARTBEAT
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QGuiApplication
import os
import time
import configparser
#PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中

from PyQt5.QtWidgets import *

#导入designer工具生成的login模块
from childwindow import Ui_ChildWindow

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QWaitCondition, QMutex, Qt

#导入设备库
from USB2IICTool import USB2IIC
from ctypes import *
from zhexiantu import *
from write_excel import *

REG_VOLT = 0x02
REG_CURRENT = 0x04
Reg_05 = [0, 0]
Reg_00 = [0x44, 0x97]
time_interval = 0.1
IICaddr=0
volt = 0
current = 0
currenlsb = 1
powername = 'ELVDD'
dirname = ''

CLK_LIST = ['100k', '200k', '400k']

IIC = USB2IIC()

power_dec = {
    'ELVDD': 'ELVDD_big',
    'ELVSS': 'ELVSS_big',
    'VDD': 'VDD_big',
    'VDDIO': 'VDDIO_big',
    'VBL': 'VBL',
    'TPVDD': 'TPVDD',
    'TPVDDIO': 'TPVDDIO',
    'VGH': 'VGH',
    'VGL': 'VGL',
}

power_list = [
    'ELVDD', 'ELVSS', 'VDD', 'VDDIO', 'VBL', 'TPVDD', 'TPVDDIO', 'VGH', 'VGL'
]


def clk_2_number(index):
    number = {0: 100000, 1: 200000, 2: 400000}
    return number.get(index, None)

def volt_value_conv(value):
    global volt
    # volt = value * 0.00125 * voltATT
    volt = value * 0.00125
    return volt

def current_value_conv(value):
    global current
    global currenlsb
    current = value * currenlsb
    return current

def time_monitor():
    global file_name
    print('************')
    name = dirname + '\\{}.csv'.format(powername)
    file_name = name
    print(file_name)

def create_dir():
    global dirname
    nowtime = time.localtime()
    strftime = time.strftime("%Y%m%d", nowtime)
    strftime_1 = time.strftime("%H_%M_%S", nowtime)
    file_1 = os.getcwd()
    name = file_1 + '\\测试数据\\{}\\九路监测数据{}'.format(strftime,strftime_1)
    dirname = name
    name = name.split('\\')
    dir = ''
    for i in range(len(name)):
        if i == len(name)-1:
            dir = dir[:-1]
            if not os.path.exists(dir):
                os.mkdir(dir)
        elif i == len(name)-2:
            dir_1 = dir[:-1]
            if not os.path.exists(dir_1):
                os.mkdir(dir_1)
            b = name[i]+'\\'
            dir = dir +b
        else:
            b = name[i]+'\\'
            dir = dir +b


config = configparser.ConfigParser()
config.read('./powerconfig.conf', encoding="utf-8")
def IIC_config(power):
    try:
        global Reg_00
        global Reg_05
        global IICaddr
        global currenlsb
        power = power_dec[power]
        IICaddr = int(config.get(power, 'iicaddr'), 16)
        # print(iicaddr)
        currenlsb = config.getfloat(power, 'CurrentLSB')
        # print(currentLSB)
        value = config.get(power, 'Reg_05').split(',')
        for i in range(len(Reg_05)):
            Reg_05[i] = int(value[i], 16)
        # print(Reg_05)

        WriteBuffer_reg00 = (c_uint8 * 3)(0x00, Reg_00[0], Reg_00[1])
        print(WriteBuffer_reg00[0], WriteBuffer_reg00[1], WriteBuffer_reg00[2])
        ret = IIC.IIC_write(IICaddr, WriteBuffer_reg00)
        # if ret == 1:
        #     a = MyChildForm()
        #     a.message_warning()
        # else:
        #     pass
        # time.sleep(0.1)
        WriteBuffer_reg05 = (c_uint8 * 3)(0x05, Reg_05[0], Reg_05[1])
        print(WriteBuffer_reg05[0], WriteBuffer_reg05[1], WriteBuffer_reg05[2])
        ret = IIC.IIC_write(IICaddr, WriteBuffer_reg05)
        # if ret == 1:
        #     a = MyChildForm()
        #     a.message_warning()
        # else:
        #     pass
        # time.sleep(0.1)

    except Exception as e:
        print(e)


class MyChildForm(QMainWindow, Ui_ChildWindow):

    def __init__(self, parent=None):

        super(MyChildForm, self).__init__(parent)
        self.setupUi(self)
        self.comboBox_CLK.addItems(CLK_LIST)
        self.pushButton_init.clicked.connect(self.dev_init)
        self.pushButtonStart.clicked.connect(self.work)
        self.pushButtonSTOP.clicked.connect(self.stop_thread)

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

    def power_config(self):
        if (self.checkBoxEnable_ELVDD.isChecked()):
            power_dec['ELVDD'] = 'ELVDD_small'
        else:
            power_dec['ELVDD'] = 'ELVDD_big'

        if (self.checkBoxEnable_ELVSS.isChecked()):
            power_dec['ELVSS'] = 'ELVSS_small'
        else:
            power_dec['ELVSS'] = 'ELVSS_big'

        if (self.checkBoxEnable_VDD.isChecked()):
            power_dec['VDD'] = 'VDD_small'
        else:
            power_dec['VDD'] = 'VDD_big'

        if (self.checkBoxEnable_VDDIO.isChecked()):
            power_dec['VDDIO'] = 'VDDIO_small'
        else:
            power_dec['VDDIO'] = 'VDDIO_big'

        print(power_dec)

    def work(self):
        try:
            global time_interval
            time_interval = (int(self.spinBoxTimeRead.value()) * 0.001) 
            self.power_config()    
            self.workThread = My_thread()
            self.workThread.show.connect(self.led_show)
            self.workThread.start()
            self.pushButtonStart.setEnabled(False)
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
                pass
                # self.message_warning()
            self.pushButtonStart.setEnabled(True)
            self.led_init()
        except Exception as e:
            print(e)
            # self.message_warning()
    
    def led_init(self):
        self.lcdNumberVolt_ELVDD.display(0)
        self.lcdNumberCurrent_ELVDD.display(0)
        self.lcdNumberVolt_ELVSS.display(0)
        self.lcdNumberCurrent_ELVSS.display(0)
        self.lcdNumberVolt_VDD.display(0)
        self.lcdNumberCurrent_VDD.display(0)
        self.lcdNumberVolt_VDDIO.display(0)
        self.lcdNumberCurrent_VDDIO.display(0)
        self.lcdNumberVolt_VBL.display(0)
        self.lcdNumberCurrent_VBL.display(0)
        self.lcdNumberVolt_TPVDD.display(0)
        self.lcdNumberCurrent_TPVDD.display(0)
        self.lcdNumberVolt_TPVDDIO.display(0)
        self.lcdNumberCurrent_TPVDDIO.display(0)
        self.lcdNumberVolt_VGH.display(0)
        self.lcdNumberCurrent_VGH.display(0)
        self.lcdNumberVolt_VGL.display(0)
        self.lcdNumberCurrent_VGL.display(0)

    def led_show(self):
        try:
            global powername
            if powername == 'ELVDD':
                self.lcdNumberVolt_ELVDD.display(volt)
                self.lcdNumberCurrent_ELVDD.display(current)
            elif powername == 'ELVSS':
                self.lcdNumberVolt_ELVSS.display(volt)
                self.lcdNumberCurrent_ELVSS.display(current)
            elif powername == 'VDD':
                self.lcdNumberVolt_VDD.display(volt)
                self.lcdNumberCurrent_VDD.display(current)
            elif powername == 'VDDIO':
                self.lcdNumberVolt_VDDIO.display(volt)
                self.lcdNumberCurrent_VDDIO.display(current)
            elif powername == 'VBL':
                self.lcdNumberVolt_VBL.display(volt)
                self.lcdNumberCurrent_VBL.display(current)
            elif powername == 'TPVDD':
                self.lcdNumberVolt_TPVDD.display(volt)
                self.lcdNumberCurrent_TPVDD.display(current)
            elif powername == 'TPVDDIO':
                self.lcdNumberVolt_TPVDDIO.display(volt)
                self.lcdNumberCurrent_TPVDDIO.display(current)
            elif powername == 'VGH':
                self.lcdNumberVolt_VGH.display(volt)
                self.lcdNumberCurrent_VGH.display(current)
            elif powername == 'VGL':
                self.lcdNumberVolt_VGL.display(volt)
                self.lcdNumberCurrent_VGL.display(current)
            else:
                pass
        except Exception as e:
            print(e)

    def message_warning(self):
        #提示
        msg_box = QMessageBox(QMessageBox.Warning, '警告', '系统异常')
        msg_box.exec_()

    def message_done(self, msg):
        #提示
        msg_box = QMessageBox(QMessageBox.Information, '提示', msg)
        msg_box.exec_()

    def closeEvent(self, event):
        self.stop_thread()

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
        global volt
        global current
        # global file_name
        global IICaddr
        global powername
        global time_interval
        create_dir()
        while 1:
            try:
                self.mutex.lock()
                for powername in power_list:
                    time_monitor()
                    excel_creart(file_name)
                    IIC_config(powername)      # 上锁
                    value_volt = IIC.power_read(IICaddr,REG_VOLT)
                    # time.sleep(0.1)
                    value_current = IIC.power_read(IICaddr,REG_CURRENT)              
                    volt = volt_value_conv(value_volt)
                    current = current_value_conv(value_current)
                    self.show.emit() 
                    excel_write(volt,current,file_name)
                    time.sleep(time_interval)
                self.mutex.unlock()     # 解锁
            except Exception as e:
                print(e)
 
    # 线程暂停
    def pause(self):
        self._isPause = True
 
    # 线程恢复
    def resume(self):
        self._isPause = False
        self.cond.wakeAll()


if __name__ == "__main__":

    # 优化不同分辨率显示
    QGuiApplication.setAttribute(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行

    app = QApplication(sys.argv)

    #初始化

    Child = MyChildForm()

    #将窗口控件显示在屏幕上

    Child.show()

    #程序运行，sys.exit方法确保程序完整退出。

    sys.exit(app.exec_())