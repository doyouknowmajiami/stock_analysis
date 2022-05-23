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
from pyecharts.charts import Bar
from pyecharts import options as opts

# 導入輸出圖片工具
from pyecharts.render import make_snapshot
# 使用snapshot-selenium 渲染圖片
from snapshot_selenium import snapshot

#畫完整K線
def draw_kline(month, values, stock_name):
    kline = (
        Kline()
        .add_xaxis(month)
        .add_yaxis(
            "kline", 
            values, 
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ec0000", #紅
                color0="#00da3c", #綠
                border_color="#8A0000",
                border_color0="#008F28",
            ),
            #當下價格的最高點
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="max", value_dim="highest")]
            ),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="日期",axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line"),is_scale=True
                                    
                                    ),
            yaxis_opts=opts.AxisOpts(name="價格",splitline_opts=opts.SplitLineOpts(is_show=True),
                                     #十字線
                                     axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line",
                                                                           linestyle_opts=opts.LineStyleOpts(type_="dashed",color="lightskyblue")),
                                     is_scale=True,
                                     splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))
                                    ),
            #讓方框只顯示y軸的值
            tooltip_opts=opts.TooltipOpts(is_show=True,axis_pointer_type= "cross",trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
            title_opts=opts.TitleOpts(title=stock_name), 
        )
    )
    return(kline)

#繪製K線圖片
def draw_kline_picture(month, values, stock_name, buy_sc, sell_sc):
    kline = (
        Kline()
        .add_xaxis(month)
        .add_yaxis(
            "kline", 
            values, 
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ec0000", #紅
                color0="#00da3c", #綠
                border_color="#8A0000",
                border_color0="#008F28",
            ),
            #當下價格的最高點
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="max", value_dim="highest")]
            ),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="日期",axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line"),is_scale=True
                                    
                                    ),
            yaxis_opts=opts.AxisOpts(name="價格",splitline_opts=opts.SplitLineOpts(is_show=True),
                                     #十字線
                                     axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line",
                                                                           linestyle_opts=opts.LineStyleOpts(type_="dashed",color="lightskyblue")),
                                     is_scale=True,
                                     splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))
                                    ),
        )
    )
    kline.overlap(buy_sc) #買入點位圖疊加
    kline.overlap(sell_sc) #賣出點位圖疊加
    # 輸出保存為圖片
    make_snapshot(snapshot, kline.render(), "kline保存圖片.png")


#計算每次交易虧損及獲利
def profit_and_loss(buy_price, sell_price):
    #每次交易虧損及獲利
    profit = []
    loss = []
    ROI = [] #累積報酬率＝總損益/投入本金
    for i in range(len(sell_price)):
        buy_tax = buy_price[i]*0.001425
        sell_tax = sell_price[i]*0.004425
        ROI.append((sell_price[i]-buy_price[i]-buy_tax-sell_tax)/(buy_price[i]+buy_tax+sell_tax))
        if (sell_price[i]-buy_price[i]-buy_tax-sell_tax) >= 0:
            profit.append(sell_price[i]-buy_price[i]-buy_tax-sell_tax)
        else:
            loss.append(sell_price[i]-buy_price[i]-buy_tax-sell_tax)
    return (profit, loss, ROI)

#在kline上進行買賣點位標記
def draw_scatter(buy_date, buy_price, sell_date, sell_price):
    #買賣點位標記
    buy_sc = (Scatter()
          .add_xaxis(buy_date)
          .add_yaxis("buy", 
                     buy_price,
                     itemstyle_opts=opts.ItemStyleOpts(
                         color="#00da3c"
                     )
                    )
         )
    sell_sc = (Scatter()
          .add_xaxis(sell_date)
          .add_yaxis("sell", 
                     sell_price,
                     itemstyle_opts=opts.ItemStyleOpts(
                         color="#ec0000"
                     )
                    )
         )
    return(buy_sc, sell_sc)

#繪製Table-1「損益分析」表
def draw_table_1(stock, profit, loss, recent_date, buy_date, buy_price, sell_date, sell_price, ROI):
    #Table-1「損益分析」
    table_1_headers = ["總損益","總獲利","總虧損","總交易次數","最大交易獲利","最大交易虧損","勝率","年化報酬率","未實現損益"]
    table_1_content = []

    # 總損益 = 每次交易的錢相加
    total_profit_and_loss = round(sum(profit) + sum(loss),2)
    table_1_content.append(str(total_profit_and_loss))
    print("總損益：%f" % (total_profit_and_loss))

    # 總獲利 = 每次賺錢的錢相加
    total_profit = round(sum(profit),2)
    table_1_content.append(str(total_profit))
    print("總獲利：%f" % (total_profit))

    # 總虧損 = 每次賠錢的錢相加
    total_loss = round(sum(loss),2)
    table_1_content.append(str(total_loss))
    print("總虧損：%f" % (total_loss))

    # 總交易次數
    total_trade_counts = round(len(sell_price),2)
    table_1_content.append(str(total_trade_counts))
    print("總交易次數：%d" % (total_trade_counts))

    # 最大交易獲利
    max_profit = round(max(profit),2)
    table_1_content.append(str(max_profit))
    print("最大交易獲利：%f" % (max_profit))

    # 最大交易虧損
    max_loss = round(min(loss),2)
    table_1_content.append(str(max_loss))
    print("最大交易虧損：%f" % (max_loss))

    # 勝率 ＝ 成功次數/(總交易次數)
    win_rate = round(len(profit) / total_trade_counts,2)
    table_1_content.append(str("{:.2%}".format(win_rate)))
    print("勝率：%f" % (win_rate))

    # 年化報酬率 ＝ (1 + 累積報酬率)^(1/年數) – 1
    closely_date = datetime.strptime(recent_date, "%Y-%m-%d").date()
    start_date = datetime.strptime('2019-01-01', "%Y-%m-%d").date()
    CAGR_year = (closely_date - start_date).days/365
    CAGR = round(pow((1 + sum(ROI)),1.0/CAGR_year) -1,2)
    table_1_content.append(str("{:.2%}".format(CAGR)))
    print("年化報酬率：%s" % ("{:.2%}".format(CAGR)))

    # 未實現損益 ＝ 最後一天收盤價 - 最後一次買入價
    if len(sell_date) == len(buy_date):
        table_1_content.append("0")
        print("未實現損益：%s" % ("0"))
        print(table_1_content)
    else:
        last_close_price = stock[(stock.date==recent_date)]["close"].values[0]
        unrealized_gain_and_loss =  round(last_close_price - (buy_price[-1]*1.004425) - (last_close_price*0.001425),2)
        table_1_content.append(str(unrealized_gain_and_loss))
        print("未實現損益：%f" % (unrealized_gain_and_loss))
        print(table_1_content)
    #1d to 2d
    table_1_content = np.reshape(table_1_content,(-1,len(table_1_content)))

    table_1 = Table()
    table_1.add(table_1_headers, table_1_content)
    table_1.set_global_opts({"title":"損益分析"})
    return(table_1)

#繪製Table-2(交易次數編號、損益、實質報酬率、實質累積報酬率、手續費、證交稅)表
def darw_table_2(stock, recent_date, buy_date, buy_price, sell_date, sell_price, ROI):
    #Table-2
    # 交易次數編號、損益、實質報酬率、實質累積報酬率、手續費、證交稅
    table_2_headers = ["交易次數編號", "買入日期", "買入價格", "賣出日期", "賣出價格", "損益", "實質報酬率", "實質累積報酬率", "手續費", "證交稅"]

    #內容
    table_2_content = []
    for i in range(len(sell_price)):
        inside_content = []
        inside_content.append(i+1) #交易次數編號
        inside_content.append(buy_date[i]) #買入日期
        inside_content.append(buy_price[i]) #買入價格
        inside_content.append(sell_date[i]) #賣出日期
        inside_content.append(sell_price[i]) #賣出價格
        last_close_price = stock[(stock.date==recent_date)]["close"].values[0]
        inside_content.append(round((sell_price[i]- (buy_price[i]*1.004425) - (last_close_price*0.001425)),2)) #損益
        inside_content.append("{:.2%}".format(ROI[i])) #實質報酬率
        inside_content.append("{:.2%}".format(sum(ROI[:(i+1)]))) #實質累積報酬率
        inside_content.append("{:.5f}".format((buy_price[i]+sell_price[i])*0.00285)) #手續費
        inside_content.append("{:.5f}".format(sell_price[i]*0.003)) #證交稅
        table_2_content.append(inside_content)
    print(pd.DataFrame(table_2_content))
    table_2 = Table()
    table_2.add(table_2_headers, table_2_content)
    table_2.set_global_opts({"title":"交易細節"})        
    return(table_2)

#表1-損益分析+K線+表2-交易細節(垂直排列)，並產出網址
def pics_combine(table_1, kline, table_2):
    final_result = Page()
    final_result.add(table_1)
    final_result.add(kline)
    final_result.add(table_2)
    final_result.render("測試.html")

# In[ ]:




