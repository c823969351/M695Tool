# -*- coding: UTF-8 -*-

import datetime
import csv
import os
import time


def excel_creart(filename):
    a = filename.split('\\')
    dir = ''
    # print(a)
    for i in range(len(a)):
        if i == len(a)-1:
            dir = dir[:-1]
            if not os.path.exists(dir):
                os.mkdir(dir)
            if not os.path.exists(filename):
                with open(filename, 'a+') as test:
                    test.write('Volt(V),Current(A)\n')
        elif i == len(a)-2:
            dir_1 = dir[:-1]
            if not os.path.exists(dir_1):
                os.mkdir(dir_1)
            b = a[i]+'\\'
            dir = dir +b
        elif i == len(a)-3:
            dir_1 = dir[:-1]
            if not os.path.exists(dir_1):
                os.mkdir(dir_1)
            b = a[i]+'\\'
            dir = dir +b
        else:
            b = a[i]+'\\'
            dir = dir +b
    
    
def excel_write(volt,current,filename):  #打印电压表
 
    with open(filename, 'a+') as test:
        test.write(str(volt) + ',' + str(current))
        test.write("\n")


