#!/usr/bin/env python
# coding: utf-8

# In[8]:

import side_project.StockLib
from side_project.StockLib.KDStockStrategy import *
from side_project.StockLib.MACDStockStrategy import *
from side_project.StockLib.MAStockStrategy import *
from side_project.StockLib.Stock_lib import *
from side_project.StockLib.BollingerBandsStockStrategy import *

from FinMind.data import DataLoader
import pandas as pd
from datetime import date 

#股市分析主程式(依據給予股票名畫出k線圖)
def stock_analysis(token, stock_name):
    #api key
    api = DataLoader()
    api.login_by_token(api_token=token)
    today = str(date.today())
    #之後提供，只回測3年，以及從2019-01-01到近期的選擇
    stock = api.taiwan_stock_daily(
        stock_id=stock_name,
        start_date='2019-01-01',
        end_date= today
    )
    recent_date = str(stock["date"].to_numpy().tolist()[-1])
    #股價的資料tolist
    values = stock[["open", "close", "min", "max"]].to_numpy().tolist()

    #月份的資料tolist
    data_m = stock[["date"]].to_numpy()
    data_m = data_m.flatten()
    month = []
    for m in data_m:
        month.append(str(m)[:10])

    #執行
    kline = draw_kline(month, values, stock_name)
    return stock, month, kline, recent_date

#股市分析主程式(在k線圖上依據交易策略繪製買賣點位,以及損益分析表)
def stock_analysis_strategy(strategy, strategy_data, strategy_name, stock_name, stock, kline, recent_date):
    #執行    
    #投資策略
    strategy()
    buy_date, buy_price, sell_date, sell_price = strategy_data() #依據策略建立買賣點位 
    profit, loss, ROI = profit_and_loss(buy_price, sell_price) #每次交易虧損、獲利、累積報酬率
    buy_sc, sell_sc = draw_scatter(buy_date, buy_price, sell_date, sell_price) #買賣點位的標記
    kline.overlap(buy_sc) #買入點位圖疊加
    kline.overlap(sell_sc) #賣出點位圖疊加
    #執行
    table_1 = draw_table_1(stock, profit, loss, recent_date, buy_date, buy_price, sell_date, sell_price, ROI) #表1-損益分析製作
    #執行
    table_2 = darw_table_2(stock, recent_date, buy_date, buy_price, sell_date, sell_price, ROI)
    #表2-交易細節製作
    #執行
    pics_combine(table_1, kline, table_2, strategy_name, stock_name) #表1-損益分析+K線+表2-交易細節(垂直排列)，並產出網址





