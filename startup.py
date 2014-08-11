#!/usr/bin/env/ python

#title:         :startup.py
#description    :analyze startup data and build regression model for each quadrant

#=========================================================================================================


import pandas as pd
import numpy as np
import os
import datetime as dt
from datetime import timedelta
import cPickle as pickle
import matplotlib.pyplot as plt
from pandas.tseries.holiday import USFederalHolidayCalendar


class Startup:
    def __init__(self, interior_temps, building):


    def read_building_temp_data(building):


    def read_weather_




def detect_startup(daily_data):

for col in daily_data.columns:
quad_data = daily_data[col]


quad_data.pct_change().max()
quad_data.pct_change().argmax()
quad_data.pct_change().min()
quad_data.pct_change().argmin()


quad_data.plot()
plt.show()

quad_data.pct_change().plot()
plt.show()


# check between 6 and 9 am
day = ts.index[0].date()
start = dt.datetime(day.year, day.month, day.day, 6)
end = dt.datetime(day.year, day.month, day.day, 9)
time_range = pd.date_range(start, end, freq='15min')


def cool_or_heat(ts, time_range):
    gradient_sum = ts.ix[time_range].pct_change().sum()


def spike_detection(ts, time_range):
    gradient_sum = ts.ix[time_range].pct_change().sum()
    if gradient_sum < 0:
        spike_time = ts.pct_change().argmin()
    else:
        spike_time = ts.pct_change().argmax()
    return spike_time








if __name__ == "__main__":

os.chdir('/home/lj/metriq')
#interior_temps = pd.read_csv('interior_temps_mat2.csv')
interior_temps = pd.read_pickle('interior_temps_mat2.p')
startup = pd.read_pickle('startup_345.p')



for col in interior_temps.columns:
    print col, min(interior_temps[col]), max(interior_temps[col])












