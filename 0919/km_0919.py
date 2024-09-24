import time
import os 
import pandas as pd
import numpy as np
import talib as ta

from sklearn.cluster import KMeans
from kneed import KneeLocator
from datetime import datetime
from datetime import timedelta

def init(context):
    context.s1 = context.run_info.base_book_id
    context.sub_dir=pd.read_csv("D:/Code/0911/subjective_prediction.csv")
    context.win_shut_str=''
    context.time_window=timedelta(days=5)
    context.on_the_window=False
    

def before_trading(context):
    context.open_condition=False
    context.long_condition=False
    context.short_condition=False
    context.close_condition1=False
    context.close_long_condition2=False
    context.close_short_condition2=False
    context.hold_long_pos=False
    context.hold_short_pos=False
    context.break_up=False
    context.break_dn=False
    context.km_upline=0
    context.dn_line=10000
    context.sub_chance=0
    direction=0
    
    portfolio = get_portfolio(context.s1,0)
    context.hold_long_pos=(portfolio.buy_quantity>0)
    context.hold_short_pos=(portfolio.sell_quantity>0)
    
    d_open  =   history_bars(context.s1, 15, '1d', 'open',True)
    d_close =   history_bars(context.s1, 15, '1d', 'close',True)
    d_high  =   history_bars(context.s1, 15, '1d', 'high',True)
    d_low   =   history_bars(context.s1, 15, '1d', 'low',True)
    if len(d_close) < 15 :
        return    
    
    d_close_diff=np.diff(d_close)
    atr=ta.ATR(d_high,d_low,d_close,timeperiod=14)
    
    get_day=context.now
    now_day=get_day.strftime('%Y-%m-%d')
    if now_day in context.sub_dir.values:
        win_shut=get_day+context.time_window
        direction=context.sub_dir[context.sub_dir['datetime'].str.contains(now_day)].iloc[0,3]
        context.open_condition=True
        context.on_the_window=True
        win_shut_str=win_shut.strftime('%Y-%m-%d')

    if now_day==context.win_shut_str:
        context.on_the_window=False
        
    if direction==1:
        context.long_condition=True
    elif direction==-1:
        context.short_condition=True
    
    if atr[-1]>1:
        context.close_condition1=True
        
    if (d_close_diff[-1]>0)&(d_close_diff[-2]>0)&(d_close_diff[-3]>0):
        context.close_long_condition2=True
    elif (d_close_diff[-1]>0)&(d_close_diff[-2]>0)&(d_close_diff[-3]>0):
        context.close_short_condition2=True

    price=history_bars(context.s1, 60, '4h', 'close',True)
    X=np.array(price)
    kmeans=KMeans(n_clusters=3).fit(X.reshape(-1,1))
    c=kmeans.predict(X.reshape(-1,1))
    min_and_max=[]
    for i in range(3):
        min_and_max.append([-np.inf,np.inf])
    for i in range(len(X)):
        cluster=c[i]
        if X[i]>min_and_max[cluster][0]:
            min_and_max[cluster][0]=X[i]
        if X[i]<min_and_max[cluster][1]:
            min_and_max[cluster][1]=X[i]
    mam_arr=np.sort((np.array(min_and_max)).flatten())
    
    def remove_close_numbers(numbers,threshold):
        result=[numbers[0]]
        for i in range(1,len(numbers)):
            if abs(numbers[i]-result[-1]) > threshold:
                result.append(numbers[i])
        return result
    
    def find_closest_numbers(numbers,target,k):
        differences=[abs(number-target) for number in numbers]
        sorted_diff=sorted(zip(numbers,differences),key=lambda x:x[1])
        closet_numbers=[number for number, _ in sorted_diff[:k]]
        return closet_numbers
    

    sup=remove_close_numbers(mam_arr,10)
    bi_sup=find_closest_numbers(numbers=sup,target=d_close[-1],k=2)
    context.km_upline=bi_sup[0]
    context.km_dnline=bi_sup[1]


        
def handle_bar(context): 

    d_close =   history_bars(context.s1, 15, '1d', 'close',True)
    if len(d_close)<16:
        return
    
    context.break_up=(d_close[-1]>context.km_upline)
    context.break_dn=(d_close[-1]<context.km_dnline)
    if context.on_the_window:
        if context.long_condition and context.open_condition and context.break_up:
            buy_open(context.s1, "market", volume=1,serial_id = 1)
            context.long_condition=False
        elif context.short_condition and context.open_condition and context.break_dn:
            sell_open(context.s1, "market", volume=1,serial_id = 2)
            context.short_condition=False
    
    if (context.close_condition1 or context.close_long_condition2) and context.hold_long_pos:
            portfolio = get_portfolio(context.s1,0)
            buy_close(context.s1,"market", volume=portfolio.buy_quantity,serial_id = 3)
            context.close_condition1=False
            context.close_long_condition2=False
    elif (context.close_condition1 or context.close_short_condition2) and context.hold_short_pos:
            portfolio = get_portfolio(context.s1,0)
            sell_close(context.s1,"market", volume=portfolio.sell_quantity,serial_id = 4)
            context.close_condition1=False
            context.close_short_condition2=False
    
def after_trading(context):
    pass