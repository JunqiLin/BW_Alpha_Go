#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 12:19:53 2019

@author: linjunqi
"""

"""
STRATEGY
"""


import pandas as pd
import numpy as np
from collections import defaultdict
import os
import sys
lib_path = os.path.abspath(os.path.join('../..'))
sys.path.append(lib_path)

from trader.constant import DIRECTION_LONG,DIRECTION_SHORT,OFFSET_OPEN,OFFSET_CLOSE 
from trader.datatool import BarManager

MAX_PRODUCT_POS = 4         # 单品种最大持仓
MAX_DIRECTION_POS = 10      # 单方向最大持仓




class TurtleResult(object):
    def __init__(self):
        self.unit = 0
        self.entry = 0
        self.exit = 0
        self.pnl = 0
    
    def open(self, price, volumn):
        cost = self.unit * self.entry
        cost += price * volumn
        self.unit += volumn
        self.entry = cost / self.unit
        
    def close(self,price):
        self.exit = price 
        self.pnl = (self.exit - self.entry)* self.unit
        
        
    
class TurtleStrategy(object):
    
    def __init__(self, portfolio, vtSymbol, 
                 entry_window, exit_window, atr_window,
                 profitCheck=False):
        self.portfolio = portfolio
        self.vtSymbol = vtSymbol
        self.entry_window = entry_window
        self.exit_window = exit_window
        self.atr_window = atr_window
        self.profitCheck = profitCheck
        
        self.core = BarManager(60)
        
        self.atrVolatility = 0
        self.entry_up = 0
        self.entry_down = 0
        self.exit_up = 0 
        self.exit_down = 0
        
        self.long_entry1 = 0
        self.long_entry2 = 0
        self.long_entry3 = 0
        self.long_entry4 = 0
        self.long_stop = 0
        
        self.short_entry1 = 0
        self.short_entry2 = 0
        self.short_entry3 = 0
        self.short_entry4 = 0
        self.short_stop = 0
        
        self.unit = 0
        self.result = None              # 当前的交易
        self.resultList = []            # 交易列表
        self.bar = None                 # 最新K线
        
        
    def onBar(self, bar):
        
        self.bar = bar
        self.core.update_bar(bar)
        if not self.core.inited:
            return
        
        self.generateSignal(bar)
        self.cal_indicator()
        
    def generateSignal(self, bar):
        
        if not self.long_entry1:
            
            return
        
        # 优先检查平仓
        if self.unit > 0:
            longExit = max(self.long_stop, self.exit_down)
            
            if bar.low <= longExit:
                self.sell(longExit)
                return
        elif self.unit < 0:
            shortExit = min(self.short_stop, self.exit_up)
            if bar.high >= shortExit:
                self.cover(shortExit)
                return
            
        if self.unit >= 0:
            
            trade = False
            
            if bar.high >= self.long_entry1 and self.unit<1:
                
                self.buy(self.long_entry1,1)
                trade = True
                
            if bar.high >= self.long_entry2 and self.unit<2:
                self.buy(self.long_entry2,1)
                trade = True
                
            if bar.high >= self.long_entry3 and self.unit<3:
                self.buy(self.long_entry3,1)
                trade = True
                
            if bar.high >= self.long_entry4 and self.unit<4:
                self.buy(self.long_entry4,1) 
                trade = True
                
            if trade:
                return
        if self.unit <=0:
            
            if bar.low <= self.short_entry1 and self.unit>-1:
                self.short(self.short_entry1,1)
                
            if bar.low <= self.short_entry2 and self.unit>-2:
                self.short(self.short_entry2,1)
                
            if bar.low <= self.short_entry3 and self.unit>-3:
                self.short(self.short_entry3,1)
                
            if bar.low <= self.short_entry4 and self.unit>-4:
                self.short(self.short_entry4,1)
                
        
    def cal_indicator(self):
        self.entry_up,self.entry_down = self.core.donchian(self.entry_window)
        self.exit_up,self.exit_down = self.core.donchian(self.exit_window)
        
        if not self.unit:
            
            self.atrVolatility = self.core.atr(self.atr_window)
            
            self.long_entry1 = self.entry_up 
            self.long_entry2 = self.entry_up + 0.5* self.atrVolatility
            self.long_entry3 = self.entry_up + 1.0* self.atrVolatility
            self.long_entry4 = self.entry_up + 1.5* self.atrVolatility
            self.long_stop = 0
            
            self.short_entry1 = self.entry_down
            self.short_entry2 = self.entry_down + 0.5* self.atrVolatility
            self.short_entry3 = self.entry_down + 1.0* self.atrVolatility
            self.short_entry4 = self.entry_down + 1.5* self.atrVolatility
            self.short_stop = 0
            
    def newSignal(self, direction, offset, price, volume):
        self.portfolio.newSignal(self, direction, offset, price, volume)
        
        
    """buy sell short cover"""
    def buy(self, price, volumn):
        price = self.cal_trade_price(price, DIRECTION_LONG)
        self.open(price,volumn)
        self.newSignal(DIRECTION_LONG, OFFSET_OPEN, price, volumn)
        self.long_stop = price - 2* self.atrVolatility
        
    def sell(self, price):
        price = self.cal_trade_price(price, DIRECTION_SHORT)
        volumn = abs(self.unit)
        self.close(price)
        self.newSignal(DIRECTION_SHORT,OFFSET_CLOSE, price, volumn)
        
    def short(self, price, volumn):
        price = self.cal_trade_price(price, DIRECTION_SHORT)
        self.open(price, -volumn)
        self.newSignal(DIRECTION_SHORT,OFFSET_OPEN, price, volumn)
        self.short_stop = price + 2* self.atrVolatility
        
    def cover(self, price):
        price = self.cal_trade_price(price, DIRECTION_LONG)
        volumn = abs(self.unit)
        self.close(price)
        self.newSignal(DIRECTION_LONG,OFFSET_CLOSE, price, volumn)
    
    def open(self, price, volumn):
        self.unit += volumn
        if not self.result:
            self.result = TurtleResult()
        self.result.open(price, volumn)
        
    def close(self, price):
        
        self.unit = 0
        self.result.close(price)
        self.resultList.append(self.result)
        self.result = None
    
            
    def getLastPnl(self):

        if not self.resultList:
            return 0
        
        result = self.resultList[-1]
        return result.pnl
            
    def cal_trade_price(self, price, direction):
        if direction == DIRECTION_LONG:
            tradePrice = max(price, self.bar.open)
        else:
            tradePrice = min(price,self.bar.open)
            
        return tradePrice
            
            
class TurtlePortfolio(object):
    """海龟组合：
       接收数据
       风控管理
       发送订单
       """
    def __init__(self, engine):
        """Constructor"""
        self.engine = engine
        
        self.signalDict = defaultdict(list)
        
        self.unitDict = {}          # 每个品种的持仓情况
        self.totalLong = 0          # 总的多头持仓
        self.totalShort = 0         # 总的空头持仓
        
        self.tradingDict = {}       # 交易中的信号字典
        
        self.sizeDict = {}          # 合约大小字典
        self.multiplierDict = {}    # 按照波动幅度计算的委托量单位字典
        self.posDict = {}           # 真实持仓量字典
        
        self.portfolioValue = 0     # 组合市值
        
        
    def init(self, portfolioValue, vtSymbolList, sizeDict):
        """"""
        self.portfolioValue = portfolioValue
        self.sizeDict = sizeDict
        
        for vtSymbol in vtSymbolList:
            signal1 = TurtleStrategy(self, vtSymbol, 20, 10, 20, True)
            signal2 = TurtleStrategy(self, vtSymbol, 55, 20, 20, False)
            
            l = self.signalDict[vtSymbol]
            l.append(signal1)
            l.append(signal2)
            
            self.unitDict[vtSymbol] = 0
            self.posDict[vtSymbol] = 0
            
    def onBar(self, bar):
        """"""
        for signal in self.signalDict[bar.vt_symbol]:
            signal.onBar(bar)
            
    def newSignal(self, signal , direction, offset, price, volume):
        """对交易信号进行过滤，符合条件的才发单执行"""
        unit = self.unitDict[signal.vtSymbol]
        
        # 如果当前无仓位，则重新根据波动幅度计算委托量单位
        if not unit:
            size = self.sizeDict[signal.vtSymbol]
            riskValue = self.portfolioValue * 0.01
            multiplier = riskValue / (signal.atrVolatility * size)
            multiplier = int(round(multiplier, 0))
            self.multiplierDict[signal.vtSymbol] = multiplier
        else:
            multiplier = self.multiplierDict[signal.vtSymbol]
            
        # 开仓
        if offset == OFFSET_OPEN:
            # 检查上一次是否为盈利
            if signal.profitCheck:
                pnl = signal.getLastPnl()
                if pnl > 0:
                    return
                
            # 买入
            if direction == DIRECTION_LONG:
                # 组合持仓不能超过上限
                if self.totalLong >= MAX_DIRECTION_POS:
                    return
                
                # 单品种持仓不能超过上限
                if self.unitDict[signal.vtSymbol] >= MAX_PRODUCT_POS:
                    return
            # 卖出
            else:
                if self.totalShort <= -MAX_DIRECTION_POS:
                    return
                
                if self.unitDict[signal.vtSymbol] <= -MAX_PRODUCT_POS:
                    return
        # 平仓
        else:
            if direction == DIRECTION_LONG:
                # 必须有空头持仓
                if unit >= 0:
                    return
                
                # 平仓数量不能超过空头持仓
                volume = min(volume, abs(unit))
            else:
                if unit <= 0:
                    return
                
                volume = min(volume, abs(unit))
        
        # 获取当前交易中的信号，如果不是本信号，则忽略
        currentSignal = self.tradingDict.get(signal.vtSymbol, None)
        if currentSignal and currentSignal is not signal:
            return
            
        # 开仓则缓存该信号的交易状态
        if offset == OFFSET_OPEN:
            self.tradingDict[signal.vtSymbol] = signal
        # 平仓则清除该信号
        else:
            self.tradingDict.pop(signal.vtSymbol)
        
        self.sendOrder(signal.vtSymbol, direction, offset, price, volume, multiplier)
        
    def sendOrder(self, vtSymbol, direction, offset, price, volume, multiplier):
        """"""
        # 计算合约持仓
        if direction == DIRECTION_LONG:
            self.unitDict[vtSymbol] += volume
            self.posDict[vtSymbol] += volume * multiplier
        else:
            self.unitDict[vtSymbol] -= volume
            self.posDict[vtSymbol] -= volume * multiplier
        
        # 计算总持仓
        self.totalLong = 0
        self.totalShort = 0
        
        for unit in self.unitDict.values():
            if unit > 0:
                self.totalLong += unit
            elif unit < 0:
                self.totalShort += unit
        
        # 向回测引擎中发单记录
        self.engine.sendOrder(vtSymbol, direction, offset, price, volume*multiplier)
        
        
        
        