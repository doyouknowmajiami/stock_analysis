#!/usr/bin/env python
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Kline, Scatter, Grid, Page
from pyecharts.components import Table
from datetime import date, datetime
import talib #投資策略
import math

def bool_strategy(stock):
    upperband, middleband, lowerband = talib.BBANDS(stock['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    stock['upperband'] = upperband
    stock['middleband'] = middleband
    stock['lowerband'] = lowerband

#1.前一天的收盤價【低於中線】而當天收盤價【大於中線】-買進；前一天的收盤價【大於中線】而當天收盤價【低於中線】-賣出
def bool_strategy_one_data(month,stock):
    #判斷當下是已經持有還是該賣出，1＝持有，0＝賣出
    judge = 0
    #計算賺賠多少
    result = 0
    #買賣日期與其收盤價
    buy_date = []
    buy_price = []
    sell_date = []
    sell_price = []

    for d in range(len(month)):
        #跳過前19天，SMA沒數值的時候
        if stock[(stock.date==month[d])]["upperband"].empty:
            continue

        upperband = stock[(stock.date==month[d])]["upperband"].values.tolist()[0]
        middleband = stock[(stock.date==month[d])]["middleband"].values.tolist()[0]
        previous_middleband = stock[(stock.date==month[d-1])]["middleband"].values.tolist()[0] #前一天的middleband
        lowerband = stock[(stock.date==month[d])]["lowerband"].values.tolist()[0]
        
        open_price = stock[(stock.date==month[d])]["open"].values.tolist()[0] #當天的開盤價
        previous_close_price = stock[(stock.date==month[d-1])]["close"].values.tolist()[0] #前一天的收盤價
        
        #前一天的收盤價【高於中線】而當天開盤價 -買進 
        if previous_close_price > previous_middleband and judge == 0:
            judge += 1
            buy_point = round(open_price,2) #買進點位 
            buy_date.append(month[d])
            buy_price.append(buy_point)
            print("買入日期：" + month[d])
            print("買入價：%s" % (buy_point))

        #前一天的收盤價【低於中線】而當天開盤價 -賣出 
        elif previous_close_price < previous_middleband and judge == 1:
            judge -= 1
            sell_point = round(open_price,2) #賣出點位 
            sell_date.append(month[d])
            sell_price.append(sell_point)
            result = result + round((sell_point - buy_point),2)
            print(type(result))
            print("賣出日期：" + month[d])
            print("賣出價：%s" % (sell_point))
            print("%s - %s = %s" % (sell_point, buy_point, round((sell_point - buy_point),2)))
            
    print("買進次數： %s" % (len(buy_price)))
    print("賣出次數： %s" % (len(sell_price)))
    print("結果 %s" % (round(result,2)))
    return(buy_date, buy_price, sell_date, sell_price)

#2.股價低於下線買進、股價高於上線賣出 
def bool_strategy_two_data(month, stock):
    #判斷當下是已經持有還是該賣出，1＝持有，0＝賣出
    judge = 0
    #計算賺賠多少
    result = 0
    #買賣日期與其收盤價
    buy_date = []
    buy_price = []
    sell_date = []
    sell_price = []

    for d in range(len(month)):
        #跳過前19天，SMA沒數值的時候
        if stock[(stock.date==month[d])]["upperband"].empty:
            continue

        upperband = stock[(stock.date==month[d])]["upperband"].values.tolist()[0]
        middleband = stock[(stock.date==month[d])]["middleband"].values.tolist()[0]
        lowerband = stock[(stock.date==month[d])]["lowerband"].values.tolist()[0]
        close_price = stock[(stock.date==month[d])]["close"].values.tolist()[0] #當天的收盤價
        max_price = stock[(stock.date==month[d])]["max"].values.tolist()[0] #當天的最高價
        min_price = stock[(stock.date==month[d])]["min"].values.tolist()[0] #當天的最低價

        #股價低於下線-買進
        if min_price <= lowerband and judge == 0:
            judge += 1
            buy_point = round(close_price,2) #買進點位
            buy_date.append(month[d])
            buy_price.append(buy_point)
            print("買入日期：" + month[d])
            print("買入價：%s" % (close_price))

        #股價高於上線-賣出
        elif max_price >= upperband and judge == 1:
            judge -= 1
            sell_point = round(close_price,2) #賣出點位
            sell_date.append(month[d])
            sell_price.append(sell_point)
            result = result + round((sell_point - buy_point),2)
            print(type(result))
            print("賣出日期：" + month[d])
            print("賣出價：%s" % (close_price))
            print("%s - %s = %s" % (sell_point, buy_point, round((sell_point - buy_point),2)))
            
    print("買進次數： %s" % (len(buy_price)))
    print("賣出次數： %s" % (len(sell_price)))
    print("結果 %s" % (round(result,2)))
    return(buy_date, buy_price, sell_date, sell_price)


# In[ ]:




