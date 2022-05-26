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

#SMA - 簡單移動平均線

#均線，5日均線 vs 20日均線
def sma_strategy(stock):
    stock['SMA5'] = talib.SMA(stock['close'], timeperiod=5)
    stock['SMA20'] = talib.SMA(stock['close'], timeperiod=20)
#均線，黃金交叉與死亡交叉的買賣資料
def sma_strategy_data(month,stock):
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
        #跳過前19天，SMA沒數值的時候
        if stock[(stock.date==d)]["SMA5"].empty or stock[(stock.date==d)]["SMA20"].empty:
            print("SMA5 or SMA20是NaN")
            continue

        SMA5 = stock[(stock.date==d)]["SMA5"].values.tolist()[0]
        SMA20 = stock[(stock.date==d)]["SMA20"].values.tolist()[0]
        close_price = stock[(stock.date==d)]["close"].values.tolist()[0] #當天的收盤價

        #定義黃金交叉 SMA5>SMA20
        if SMA5 > SMA20 and judge == 0:
            judge += 1
            buy_point = round(close_price,2) #買進點位
            buy_date.append(d)
            buy_price.append(buy_point)
            print("買入日期：" + d)
            print("買入價：%s" % (close_price))

        #定義死亡交叉 SMA20>SMA5
        elif SMA5 < SMA20 and judge == 1:
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


# In[2]:


#EMA - 指數平滑移動平均線
#均線，5日均線 vs 20日均線
def ema_strategy(stock):
    stock['EMA5'] = talib.EMA(stock['close'], timeperiod=5)
    stock['EMA20'] = talib.EMA(stock['close'], timeperiod=20)

def ema_strategy_data(month,stock):
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
        #跳過前19天，EMA沒數值的時候
        if stock[(stock.date==d)]["EMA5"].empty or stock[(stock.date==d)]["EMA20"].empty:
            print("EMA5 or EMA20是NaN")
            continue

        EMA5 = stock[(stock.date==d)]["EMA5"].values.tolist()[0]
        EMA20 = stock[(stock.date==d)]["EMA20"].values.tolist()[0]
        close_price = stock[(stock.date==d)]["close"].values.tolist()[0] #當天的收盤價

        #定義黃金交叉 EMA5>EMA20
        if EMA5 > EMA20 and judge == 0:
            judge += 1
            buy_point = round(close_price,2) #買進點位
            buy_date.append(d)
            buy_price.append(buy_point)
            print("買入日期：" + d)
            print("買入價：%s" % (close_price))

        #定義死亡交叉 EMA20>EMA5
        elif EMA5 < EMA20 and judge == 1:
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


# In[ ]:




