#!/usr/bin/env python
# coding: utf-8

# In[13]:


import pandas as pd
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Kline, Scatter, Grid, Page
from pyecharts.components import Table
from datetime import date, datetime
import talib #投資策略
import math

#MACD投資策略

#求出DIF、DEM、以及MACD值
def macd_strategy(stock):
    stock['DIF'],stock['MACD'],stock['DIF-MACD'] = talib.MACD(stock['close'].to_numpy(),
                                                         fastperiod=12,
                                                         slowperiod=26,
                                                         signalperiod=9)
#定義快線與慢線之間的交互關係與交易點位
def macd_strategy_data(month,stock):
    #判斷當下是已經持有還是該賣出，1＝持有，0＝賣出
    judge = 0
    #計算賺賠多少
    result = 0
    #買賣日期與其收盤價
    buy_date = []
    buy_price = []
    sell_date = []
    sell_price = []

    for d in month:
        #跳過前33(26+9)天，MACD沒數值的時候
        if stock[(stock.date==d)]["DIF"].empty or stock[(stock.date==d)]["MACD"].empty or stock[(stock.date==d)]["DIF-MACD"].empty:
            print("DIF or MACD or D-M 是NaN")
            continue

        D_M = stock[(stock.date==d)]["DIF-MACD"].values.tolist()[0]
        close_price = stock[(stock.date==d)]["close"].values.tolist()[0] #當天的收盤價

        #定義快線>慢線 D-M>0 買進訊號
        if D_M>0 and judge == 0:
            judge += 1
            buy_point = round(close_price,2) #買進點位
            buy_date.append(d)
            buy_price.append(buy_point)
            print("買入日期：" + d)
            print("買入價：%s" % (close_price))

        #定義慢線>快線 D-M<0 賣出訊號
        elif D_M<0 and judge == 1:
            judge -= 1
            sell_point = round(close_price,2) #買進點位
            sell_date.append(d)
            sell_price.append(sell_point)
            result = result + round((sell_point - buy_point),2)
            print(type(result))
            print("賣出日期：" + d)
            print("賣出價：%s" % (close_price))
            print("%s - %s = %s" % (sell_point, buy_point, round((sell_point - buy_point),2)))
    print("買進次數： %s" % (len(buy_price)))
    print("賣出次數： %s" % (len(sell_price)))
    print("結果 %s" % (round(result,2)))
    return(buy_date, buy_price, sell_date, sell_price)
