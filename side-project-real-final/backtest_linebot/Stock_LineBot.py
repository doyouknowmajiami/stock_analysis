#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

import pandas as pd
from FinMind.data import DataLoader 
import numpy as np
import time
from datetime import datetime
import re
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

#抓取台股所有的股票id
token = config.get('stock', 'token')
api = DataLoader()
api.login_by_token(api_token=token)
df = api.taiwan_stock_info()

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

#股票與交易策略，基本資料
id_storage = {"id":[]}
list_strategy = ["SMA","EMA","KD","MACD","BOOL_1","BOOL_2"] #目前有提供的交易策略
list_stock_id = np.unique(df["stock_id"].values).tolist()
user_reply_category = ["time_record","user_text_stock","user_text_strategy", "user_text_email", "Mode"]
strategy_detail = {
    "SMA":"以SMA的「5日均線」與「20日均線」交叉作為買賣的依據，當5日>20日 - 當天收盤價買進，當5日<20日 - 當天收盤價賣出",
    "EMA":"以EMA的「5日均線」與「20日均線」交叉作為買賣的依據，當5日>20日 - 當天收盤價買進，當5日<20日 - 當天收盤價賣出",
    "KD":"以KD的「K線」與「D線」交叉作為買賣的依據，當K值>D值,為黃金交叉 - 當天收盤價買進，當K值<D值,為死亡交叉 - 當天收盤價賣出；以20天取RSV值,再分別以5天取出K、D值為例",
    "MACD":"以「DIF」與「MACD」的差值作為買賣依據，當快線>慢線(DIF>MACD，D-M>0) - 當天收盤價買進；當快線<慢線(DIF<MACD，D-M<0) - 當天收盤價買出，DIF(快線)是由12日EMA與26日EMA相減求出，MACD(慢線)則由9日DIF的EMA求出",
    "BOOL_1":"20日均線為基準取兩個標準差，算出上下線，前一天的「收盤價高於中線」- 當天開盤價買進；\n前一天的「收盤價低於中線」- 當天開盤價賣出",
    "BOOL_2":"20日均線為基準取兩個標準差，算出上下線，前一天「收盤價低於下線」- 當天開盤價買進；\n前一天「收盤價高於上線」- 當天開盤價賣出"
}


from side_project.stock_analysis_drawkline import *
def back_testing(stock_name, user_strategy):
    stock, month, kline, recent_date = stock_analysis(token, stock_name)
    strategy_func = {
        "SMA":[lambda :sma_strategy(stock),lambda :sma_strategy_data(month, stock)],
        "EMA":[lambda :ema_strategy(stock),lambda :ema_strategy_data(month, stock)],
        "KD":[lambda :kd_strategy(stock),lambda :kd_strategy_data(month, stock)],
        "MACD":[lambda :macd_strategy(stock),lambda :macd_strategy_data(month, stock)],
        "BOOL_1":[lambda :bool_strategy(stock),lambda :bool_strategy_one_data(month, stock)],
        "BOOL_2":[lambda :bool_strategy(stock),lambda :bool_strategy_two_data(month, stock)]}
    
    stock_analysis_strategy(strategy_func[user_strategy][0], strategy_func[user_strategy][1], user_strategy, stock_name, stock, kline, recent_date)


# In[ ]:


def backtesting_result(event,receiver):
    user_text = event.message.text#股票代碼與股票策略之間請加入空格
    user_text_id = []
    user_text_strategy = []
    #確認股票策略
    for i in list_strategy:
        if i in user_text or i.lower() in user_text:
            user_text_strategy.append(i)
    #確認股票資訊
    try:
        space_position = user_text.index(" ")
        user_text = user_text[0:space_position]
    except:
        user_text = user_text
        
    if user_text in list_stock_id:
        user_text_id.append(user_text)
    else:
        for i in list_stock_id:
            if i in user_text:
                user_text_id.append(i)
    
    
    #找不到相對應的股票        
    if len(user_text_id) == 0:
        if len(user_text_strategy) == 0:
        #找不到相對應的投資策略
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【查無此股票ID】且【查無此投資策略】\n 請重新輸入"))
        elif len(user_text_strategy) >= 2:
            #用戶輸入了2個以上的股票
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【查無此股票ID】且【一次只能查詢一種投資策略】\n 請重新輸入"))
        else:
            #有找到相對應的投資策略
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【查無此股票ID】但【投資策略輸入正確】\n 請重新輸入"))
    #用戶輸入了2個以上的股票
    elif len(user_text_id) >= 2:
        #找不到相對應的投資策略
        if len(user_text_strategy) == 0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【一次只能查詢一支股票】且【查無此投資策略】\n 請重新輸入"))
        elif len(user_text_strategy) >= 2:
            #用戶輸入了2個以上的股票
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【一次只能查詢一支股票】且【一次只能查詢一種投資策略】\n 請重新輸入"))
        else:
            #有找到相對應的投資策略
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【一次只能查詢一支股票】但【投資策略輸入正確】\n 請重新輸入"))
    else: #用戶輸入正確
        #找不到相對應的投資策略
        if len(user_text_strategy) == 0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【股票輸入正確】但【查無此投資策略】\n 請重新輸入"))
        elif len(user_text_strategy) >= 2:
            #用戶輸入了2個以上的股票
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【股票輸入正確】但【一次只能查詢一種投資策略】\n 請重新輸入"))
        else:
            #有找到相對應的投資策略 *這部分到時候要修改為，回傳回測結果*
            back_testing(user_text_id[0], user_text_strategy[0])
            send_results(receiver, user_text_id[0], user_text_strategy[0])
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="【股票輸入正確】且【投資策略輸入正確】\n 股票回測已傳送......"))


# In[ ]:


def new_or_old(id_storage, user_id, user_reply_category, service_name):
    #用戶是第一次使用查詢系統
    if user_id not in id_storage["id"]:
        id_storage["id"].append(user_id) #要判斷id是否存在過
        id_storage[user_id] = {}
        for i in user_reply_category:
            id_storage[user_id][i] = 0
        id_storage[user_id]["time_record"]=[]#使用股票查系統次數
        id_storage[user_id]["time_record"].append(datetime.now())
        id_storage[user_id]["Mode"] = service_name #表示用戶目前開啟的服務
        return(id_storage)
    #用戶不是第一次使用查詢系統
    else:
        id_storage[user_id]["time_record"].append(datetime.now())
        id_storage[user_id]["Mode"] = service_name
        return(id_storage)


def define_bot(id_storage,user_id,reply_content,event):
    #最近的時間 - 最近時間往回推的第五次的時間
    if len(id_storage[user_id]["time_record"]) >= 5:
        time_check = (id_storage[user_id]["time_record"][-1] - id_storage[user_id]["time_record"][-5]).seconds
    else:
        time_check = 20
    #時間差在10秒內的，判斷為機器人
    if len(id_storage[user_id]["time_record"]) % 1 == 0 and time_check <= 10:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="【系統在短時間內接受到過多的請求，系統將暫停使用%d秒鐘，待系統冷卻時間過後請再次送出訊息】"
                            (len(id_storage[user_id]["time_record"])*10)))
        time.sleep(len(id_storage[user_id]["time_record"])*10)
    #非機器人，則回傳以下訊息
    elif isinstance(reply_content, str):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_content))
    else:
        reply_content()

def email_format(email_text):
    email_formating = re.search('[\w]+@[\w]+.com[.]*[a-zA-Z]*', email_text)
    email_count = re.findall('[\w]+@[\w]+.com[.]*[a-zA-Z]*', email_text)
    if email_formating and len(email_count) == 1:
        return True
    else:
        return False
    


# In[ ]:


def search_system(event):
    global id_storage
    user_text = event.message.text
    user_id = str(event.source.user_id)
    #如果用戶輸入「查詢股票代碼」，回覆「請輸入您想查詢的股票代碼」
    if user_text == "查詢股票代碼":
        #判斷是否為第一次使用查詢系統
        id_storage = new_or_old(id_storage, user_id, user_reply_category, "stock")
        #用戶重複輸入太多次，系統暫停
        define_bot(id_storage,user_id,"【請輸入您想查詢的股票代碼】",event)

    #如果用戶輸入「查詢投資策略細節」，回覆「請輸入您想查詢的投資策略」
    elif user_text == "查詢投資策略細節":
        #判斷是否為第一次使用查詢系統
        id_storage = new_or_old(id_storage, user_id, user_reply_category, "strategy")
        #用戶重複輸入太多次，系統暫停
        define_bot(id_storage,user_id,"【請輸入您想查詢的投資策略】",event)

    #如果用戶輸入「查詢投資策略」，回覆「目前有提供的投資策略」
    elif user_text == "查詢投資策略": 
        #判斷是否為第一次使用查詢系統
        id_storage = new_or_old(id_storage, user_id, user_reply_category, "")
        define_bot(id_storage,user_id,", ".join(str(x) for x in strategy_detail),event)
    
    #如果用戶輸入「我要提供Email」，回覆「目前有提供的投資策略」
    elif user_text == "我要提供Email": 
        #判斷是否為第一次使用查詢系統
        id_storage = new_or_old(id_storage, user_id, user_reply_category, "email")
        define_bot(id_storage,user_id,"【請輸入您的Email】",event)
    
    #如果用戶輸入「請告訴我使用規則」，回覆「目前有提供的投資策略」
    elif user_text == "請告訴我使用規則": 
        #判斷是否為第一次使用查詢系統
        id_storage = new_or_old(id_storage, user_id, user_reply_category, "")
        content = """使用規則介紹：
👉🏻點選「股票代碼」後，請輸入一個您想查詢之「股票的股票代碼」，輸入後，將會回傳告知此股票本平台是否提供。
👉🏻點選「投資策略」後，將會回傳目前本平台用於回測的投資策略。
👉🏻點選「投資策略細節」後，請再輸入一種您想查詢之投資策略，輸入後，將會回傳告知該投資策略在回測中，是如何被運用的。
👉🏻點選「提供信箱」後，請輸入一個您想用來「接收回測結果的電子信箱」。

🔶股票回測的買賣單位是一張股票🔶
🟥日期是從2019/01/01到傳訊息當下的前一天開盤日🟥
★使用回測服務前，【一定要提供電子信箱】，因回傳結果是html檔
☆使用回測服務的輸入格式為：
”股票代碼”+”一個空格”+“投資策略” 
（加號以及雙引號在輸入時請省略）"""
        define_bot(id_storage, user_id, content,event)
    
    #用戶在查詢回測資訊前，須先提供email
    elif " " in user_text and isinstance(id_storage[user_id]["user_text_email"], str):
        id_storage[user_id]["time_record"].append(datetime.now())
        receiver = id_storage[user_id]["user_text_email"]
        define_bot(id_storage,user_id,lambda :backtesting_result(event, receiver),event)

    #當用戶再次輸入欲查詢的「股票代碼」，則回覆1.查無此股票 2.一次只能查詢一支股票 3.已找到相關股票 股票代碼+股票中文名
    #用戶在使用查詢系統
    elif " " not in user_text and user_id in id_storage["id"]:
        id_storage[user_id]["time_record"].append(datetime.now())
        #用戶在查詢股票
        if id_storage[user_id]["Mode"] == "stock":
            id_storage[user_id]["user_text_stock"] = []
            #分析文字中是否包含股票代碼
            try:
                space_position = user_text.index(" ")
                user_text = user_text[0:space_position]
            except:
                user_text = user_text
                
            if user_text in list_stock_id:
                id_storage[user_id]["user_text_stock"].append(user_text)
            else:
                for i in list_stock_id:
                    if i in user_text:
                        id_storage[user_id]["user_text_stock"].append(i)

            #1.查無此股票 
            if len(id_storage[user_id]["user_text_stock"]) == 0:
                define_bot(id_storage, user_id,"【查無此股票】",event)
            #2.一次只能查詢一支股票 
            elif len(id_storage[user_id]["user_text_stock"]) >= 2:
                define_bot(id_storage, user_id,"【一次只能查詢一支股票】",event)
            #3.已找到相關股票 股票代碼+股票中文名
            else:
                user_stock_id = id_storage[user_id]["user_text_stock"][0]
                stock_name = df[(df.stock_id == user_stock_id)]["stock_name"].tolist()[0]
                content = "為您查詢到股票【%s, %s】" % (user_stock_id, stock_name)

                define_bot(id_storage, user_id, content,event)

        #當用戶再次輸入欲查詢的「投資策略」，則回覆1.查無此投資策略 2.一次只能查詢一種投資策略 3.已找到相關投資策略 投資策略+投資策略說明
        #用戶在查詢投資策略
        elif id_storage[user_id]["Mode"] == "strategy":
            id_storage[user_id]["user_text_strategy"] = []
            #分析文字中是否包含投資策略
            for i in list_strategy:
                if i in user_text:
                    id_storage[user_id]["user_text_strategy"].append(i)
            #1.查無此投資策略 
            if len(id_storage[user_id]["user_text_strategy"]) == 0:
                define_bot(id_storage, user_id, "【查無此投資策略】",event)
            #2.一次只能查詢一種投資策略 
            elif len(id_storage[user_id]["user_text_strategy"]) >= 2:
                define_bot(id_storage, user_id, "【一次只能查詢一種投資策略】",event)
            #3.已找到相關投資策略 投資策略+投資策略說明
            else:
                content = strategy_detail[id_storage[user_id]["user_text_strategy"][0]]
                define_bot(id_storage, user_id, content,event)
        
        #用戶要輸入email
        elif id_storage[user_id]["Mode"] == "email":
            id_storage[user_id]["user_text_email"] = user_text
            #判斷用戶提供的email格式，是否正確
            if email_format(user_text):
                define_bot(id_storage, user_id, "【感謝您提供相關電子郵箱】",event)
                id_storage[user_id]["Mode"] = ""
            #用戶亂給email，就將儲存空間變成空的list
            else:
                id_storage[user_id]["user_text_email"] = []
                define_bot(id_storage, user_id, "【很抱歉！您所提供的電子郵箱格式並不正確】",event)
            
        elif id_storage[user_id]["Mode"] == "other" or id_storage[user_id]["Mode"] == "":
            #用戶重複輸入太多次，系統暫停
            define_bot(id_storage, user_id, "【請按照最初傳給您的訊息來啟用相關服務】",event)
    #用戶隨意輸入
    else:
        #判斷是否為第一次使用查詢系統
        id_storage = new_or_old(id_storage, user_id, user_reply_category, "other")
        #用戶重複輸入太多次，系統暫停
        define_bot(id_storage, user_id, "【請按照最初傳給您的訊息來啟用相關服務】",event)

    print(id_storage)



# In[ ]:


def send_results(receiver, stock_name, strategy_name):
    email_gmail = config.get('gmail', 'account')
    email_PW = config.get('gmail', 'token')

    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "這是股票%s 使用%s策略的回測結果" % (stock_name, strategy_name) #郵件標題
    content['Body'] = "find the attachment"
    content["from"] = "ben83925@gmail.com"  #寄件者
    content["to"] = receiver #收件者

    attachment = "%s_%s策略回測.html" % (stock_name, strategy_name)
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(attachment, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=attachment)
    content.attach(part)

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(email_gmail, email_PW)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)
        
    if os.path.exists(attachment):
        os.remove(attachment)
        print("The file has been deleted successfully")
    else:
        print("The file does not exist!")
        
        
        

