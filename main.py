import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon,QGuiApplication
#PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中

from PyQt5.QtWidgets import *

#导入designer工具生成的login模块

from mainwin import MyMainForm
from childwin import MyChildForm

from PyQt5.QtCore import Qt

if __name__ == "__main__":
    
    # 优化不同分辨率显示
    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行

    app = QApplication(sys.argv)

    #初始化

    myWin = MyMainForm()
    Child = MyChildForm()
    myWin.pushButton_9lane.clicked.connect(Child.show)


    #将窗口控件显示在屏幕上

    myWin.show()

    #程序运行，sys.exit方法确保程序完整退出。

    sys.exit(app.exec_())