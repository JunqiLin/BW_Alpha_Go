#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 15:18:01 2019

@author: linjunqi
"""



import pandas as pd
import numpy as np
import os
import talib

class BarManager(object):
    def __init__(self, size=100):
        self.count = 0
        self.size = size
        self.inited = True
        
        self.open_array = np.zeros(size)
        self.close_array = np.zeros(size)
        self.high_array = np.zeros(size)
        self.low_array = np.zeros(size)
        self.volume_array = np.zeros(size)
        
    def update_bar(self,bar):
        self.open_array[:-1] = self.open_array[1:]
        self.close_array[:-1] = self.close_array[1:]
        self.high_array[:-1] = self.high_array[1:]
        self.low_array[:-1] = self.low_array[1:]
        self.volume_array[:-1] = self.volume_array[1:]
        
        self.open_array[-1] = bar.open
        self.close_array[-1] = bar.close
        self.high_array[-1] = bar.high
        self.low_array[-1] = bar.low
        self.volume_array[-1] = bar.volume
        
    @property
    def open(self):
        return self.open_array
    
    @property
    def close(self):
        return self.close_array
    
    @property
    def high(self):
        return self.high_array
    
    @property
    def low(self):
        return self.low_array
    
    @property
    def volumn(self):
        return self.volume_array
    
    def atr(self, n, array = False):
        result = talib.ATR(self.high, self.low, self.close, n)
        
        if array:
            return result
        return result[-1]
            
    
    def donchian(self, n, array = False):
        up = talib.MAX(self.high, n)
        down = talib.MIN(self.low, n)
        
        if array:
            return up, down
        return up[-1],down[-1]
    
    
        
        