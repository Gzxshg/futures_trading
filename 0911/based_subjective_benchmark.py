import time
import os 
import pandas as pd
import numpy as np
import talib as ta

from datetime import datetime

def init(context):
    context.s1 = context.run_info.base_book_id
    context.sub_dir=pd.read_csv("D:/Code/0911/subjective_prediction.csv")
    

def before_trading(context):
    context.open_condition=False
    context.long_condition=False
    context.short_condition=False
    context.close_condition1=False
    context.close_long_condition2=False
    context.close_short_condition2=False
    context.hold_long_pos=False
    context.hold_short_pos=False
    context.sub_chance=0
    direction=''
    
    portfolio = get_portfolio(context.s1,0)
    context.hold_long_pos=(portfolio.buy_quantity>0)
    context.hold_short_pos=(portfolio.sell_quantity>0)
    
    d_open=history_bars(context.s1, 15, '1d', 'open',True)
    d_close = history_bars(context.s1, 15, '1d', 'close',True)
    d_high=history_bars(context.s1, 15, '1d', 'high',True)
    d_low=history_bars(context.s1, 15, '1d', 'low',True)
    if len(d_close) < 15 :
        return    
    
    m1_up=d_close[-1]-d_open[-1]
    m2_up=d_close[-2]-d_open[-2]
    m3_up=d_close[-3]-d_open[-3]
    atr=ta.ATR(d_high,d_low,d_close,timeperiod=14)
    
    get_day=context.now
    now_day=get_day.strftime('%Y-%m-%d')
    if now_day in context.sub_dir.values:
        direction=context.sub_dir[context.sub_dir['datetime'].str.contains(now_day)].iloc[0,3]
        context.open_condition=True
        
    if direction==1:
        context.sub_chance=1
    elif direction==-1:
        context.sub_chance=-1
    

    if context.sub_chance==1:
        context.long_condition=True
    elif context.sub_chance==-1:
        context.short_condition=True
    
    if atr[-1]>1:
        context.close_condition1=True
        
    if (m1_up>0)&(m2_up>0)&(m3_up>0):
        context.close_long_condition2=True
    elif (m1_up<0)&(m2_up<0)&(m3_up<0):
        context.close_short_condition2=True

            
        
def handle_bar(context): 
    if context.long_condition and context.open_condition:
        buy_open(context.s1, "market", volume=1,serial_id = 1)
        context.long_condition=False
    elif context.short_condition and context.open_condition:
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