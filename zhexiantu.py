# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np 

# df = pd.read_csv('电源测试20220906-13-24-06.csv')
# print(df)
# print(df.loc[0])
# # df = df.cumsum()
# print(df)
# df.plot(x = 'Volt(V)',y = 'Getvolt(V)',grid =True)
# # plt.plot([3,4,5],[2,3,2])
# plt.show()

# 当前选用matplotlib版本3.3.2
from ast import arg
from sys import argv
import matplotlib.pyplot as plt
import random
import pandas
 
class line_chart:
    def __init__(self,file_name = '电源测试.csv'):
        self.df = pandas.read_csv(file_name)
        self.power_name = self.df.columns.values[0]
        self.main()
        self.obsX = list(self.df.loc[:,'Volt(V)'])
        self.obsY = list(self.df.loc[:,'Getvolt(V)'])

    def main(self):
        # 创建一个折线图
        fig = plt.figure()
        
        # 设置中文语言
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建四个表格，411代表创建4行1列，当前在1的位置
        # ax = fig.add_subplot(4, 1, 1)
        self.bx = fig.add_subplot()
        # cx = fig.add_subplot(4, 1, 3)
        # dx = fig.add_subplot(4, 1, 4)
        
        # 给表的Y轴位置加上标签，rotation代表让文字横着展示，labelpad代表文字距表格多远了
        # ax.set_ylabel('表一', rotation=0, fontsize=16, labelpad=20)
        self.bx.set_ylabel('{}'.format(self.power_name), rotation=0, fontsize=16, labelpad=20)
        self.bx.set_xlabel('设置电压值', rotation=0, fontsize=10, labelpad=10)
        self.bx.set_ylabel('获得电压值', rotation=90, fontsize=10, labelpad=10)
    
    def drew(self):
        # 给定一个参数，用来标识是不是第一次创建
        line = None
        
        # 给定一个X轴和Y轴的参数列表，用作后面承载数据
        
        # 再给定一个X轴的开始位置，用作后面累加
        # i = volt
        
        # 往列表插入展示的点的坐标
        # self.obsX.append(i)
        # Y轴的话，由于没有实际数据，这里就用随机数代替
        # self.obsY.append(get_volt)
    
        # 如果图还没有画，则创建一个画图
        if line is None:
            # -代表用横线画，g代表线的颜色是绿色，.代表，画图的关键点，用点代替。也可以用*，代表关键点为五角星
            line = self.bx.plot(self.obsX, self.obsY, '-g', marker='.')[0]
    
        # 这里插入需要画图的参数，由于图线，是由很多个点组成的，所以这里需要的是一个列表
        line.set_xdata(self.obsX)
        line.set_ydata(self.obsY)
    
        # 我这里设计了一种方法，当X轴跑了100次的时候，则让X坐标的原点动起来
        # if len(self.obsX) < 100:
        #     self.bx.set_xlim([min(self.obsX), max(self.obsX) + 30])
        # else:
        #     self.bx.set_xlim([self.obsX[-80], max(self.obsX) * 1.2])
    
        # Y轴的话我就没让他动了，然后加一个10，防止最高的订单顶到天花板
        # self.bx.set_ylim([min(self.obsY), max(self.obsY) + 10])
    
        # 这个就是表的刷新时间了，以秒为单位
        # plt.pause(0.001)
        
        for a,b in zip(self.obsX,self.obsY):
            t = "VOLT:"+str(b)
            plt.text(a,b,t,ha='center', va='bottom', fontsize=10)
        plt.show()
    
        # 画完一次了，i的数据加1，让X轴可以一直往前走。
        # i += 1
    
    # 我这里只给了表二的数据，只是打个样，聪明的你肯定会举一反三的。

if __name__ == "__main__":
    line = line_chart('电源测试20220906-13-24-06.csv')
    line.drew()
    # while True:
    #     b = input()
    #     c = input()
    #     print(b,c)
    #     line.drew(b,c)
    # df = pandas.read_csv('电源测试20220906-13-24-06.csv')
    # x = list(df.loc[:,'Volt(V)'])
    # y = list(df.loc[:,'Getvolt(V)'])
    # z = list(df.loc[1,0])
    # print(df.columns.values[0])
    # print(z)

    
    