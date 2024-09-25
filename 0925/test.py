import pandas as pd
import numpy as np
import os
import time
import talib as ta

from datetime import datetime,date,timedelta
from tqsdk import TqApi,TqAuth,TqBacktest,TqSim,TargetPosTask
from sklearn.cluster import KMeans
from kneed import KneeLocator

api=TqApi(web_gui="http://192.168.1.186:48888",auth=TqAuth("18049858285","18049858285wk"))

d_klines=api.get_kline_serial(symbol="SHFE.rb2501",duration_seconds=86400)
fifmin_klines=api.get_kline_serial(symbol="SHFE.rb2501",duration_seconds=900)
fifmin_close=fifmin_klines['close']
price=fifmin_close[-60:]