import time
import os 
import csv
import numpy 
import talib as ta

def init(context):
    context.s1 = context.run_info.base_book_id
    context.long_period = 10
    context.short_period = 5


def before_trading(context):
    context.open_condition1=False
    context.open_condition2=False
    context.close_condition1=False
    context.close_condition2=False
    
    portfolio = get_portfolio(context.s1,0)
    context.hold_pos=(portfolio.buy_quantity>0)
    
    d_close = history_bars(context.s1, 15, '1d', 'close',True)
    d_high=history_bars(context.s1, 15, '1d', 'high',True)
    d_low=history_bars(context.s1, 15, '1d', 'high',True)
    
    if len(d_close) < 15 :
        return
        
    m1_up=d_close[-1]-d_close[-2]
    m2_up=d_close[-2]-d_close[-3]
    m3_up=d_close[-3]-d_close[-4]
    ma5 = ta.SMA(d_close,context.short_period)
    ma10 = ta.SMA(d_close,context.long_period)
    atr=ta.ATR(d_high,d_low,d_close,timeperiod=14)
    
    
    if ma5[-1]>ma10[-1] and ma5[-2]<ma10[-2]:
        context.open_condition1=True
    
    if atr[-1]>1:
        context.close_condition1=True
        
    if (m1_up>0)&(m2_up>0)&(m3_up>0):
        context.close_condition2=True
            
        
def handle_bar(context):
    fimin_close = history_bars(context.s1, 21, 'self', 'close',True)
    if len(fimin_close) < 21 :
        return
    upperband, middleband, lowerband = ta.BBANDS(fimin_close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    
    if fimin_close[-1]<lowerband[-1]:
        context.open_condition2=True
        
    if context.open_condition1 and context.open_condition2:
        buy_open(context.s1, "market", volume=100,serial_id = 1)
        context.open_condition1=False
        context.open_condition2=False
    if (context.close_condition1 or context.close_condition2) and context.hold_pos:
        portfolio = get_portfolio(context.s1,0)
        sell_close(context.s1,"market", volume=portfolio.buy_quantity,serial_id = 2)
        context.close_condition1=False
        context.close_condition2=False
    
def after_trading(context):
    pass