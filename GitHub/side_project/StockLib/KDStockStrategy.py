#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Kline, Scatter, Grid, Page
from pyecharts.components import Table
from datetime import date, datetime
import talib #投資策略
import math

#求出K以及D值(以20,5天為例)
def kd_strategy(stock):
    stock['slowk'],stock['slowd'] = talib.STOCH(stock['max'].values,
                                                stock['min'].values,
                                                stock['close'].values,
                                                         fastk_period=20,
                                                         slowk_period=5,
                                                         slowk_matype=1,
                                                         slowd_period=5,
                                                         slowd_matype=1)
#定義K線與D線之間的交互關係與交易點位
def kd_strategy_data(month,stock):
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
        #跳過前12(9+3)天，KD沒數值的時候
        if stock[(stock.date==d)]["slowk"].empty or stock[(stock.date==d)]["slowd"].empty:
            print("k值 or d值 是NaN")
            continue

        K = stock[(stock.date==d)]["slowk"].values.tolist()[0]
        D = stock[(stock.date==d)]["slowd"].values.tolist()[0]
        close_price = stock[(stock.date==d)]["close"].values.tolist()[0] #當天的收盤價

        #定義黃金交叉 K線>D線 買進訊號
        if K>D and judge == 0:
            judge += 1
            buy_point = round(close_price,2) #買進點位
            buy_date.append(d)
            buy_price.append(buy_point)
            print("買入日期：" + d)
            print("買入價：%s" % (close_price))

        #定義死亡交叉 K線<D線 賣出訊號
        elif K<D and judge == 1:
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
