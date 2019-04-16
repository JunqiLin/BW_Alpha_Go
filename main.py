#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 15:23:35 2019

@author: linjunqi
"""

import os, sys
lib_path = os.path.abspath(os.path.join('.'))
sys.path.append(lib_path)
from Alphapy.app.backtest_engine import BacktestingEngine
from datetime import datetime

engine = BacktestingEngine()

path = lib_path+'/Alphapy/data/setting.csv'
#print(path)
engine.initPortfolio(path)
start = datetime.strptime("2013-10-18 00:00:00", "%Y-%m-%d %H:%M:%S")
stop = datetime.strptime("2019-1-1 00:00:00", "%Y-%m-%d %H:%M:%S")

engine.setPeriod(start,stop)
engine.loadData()
engine.runBacktesting()
engine.showResult()

