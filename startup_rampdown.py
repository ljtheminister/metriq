import pandas as pd
import numpy as np
import os
import datetime as dt
from datetime import timedelta
import cPickle as pickle
import matplotlib.pyplot as plt

os.chdir('/home/lj/metriq/345')

## Interior Space Air Temperatures
#345---------001BMSHVATEMSPA---VAL001.csv
pre = '345---------001BMS'
post = '---VAL001'
temp_int = pd.read_csv('%s%s%s.csv'%(pre, 'HVATEMSPA', post))

## Perimeter Temperatures
#345---------001BMSHVATEMPSP---VAL001.csv
temp_per = pd.read_csv('%s%s%s.csv'%(pre, 'HVATEMPSP', post))

def find_15min_interval_before(date_string):
    d = dt.datetime.strptime(date_string, date_fmt)
    d -= timedelta(minutes=15)
    return dt.datetime(d.year, d.month, d.day, d.hour, d.minute)
    
def find_15min_interval_after(date_string):
    d = dt.datetime.strptime(date_string, date_fmt)
    d += timedelta(minutes=15)
    return dt.datetime(d.year, d.month, d.day, d.hour, d.minute)

# Group the Interior Temperatrue Data - Groupby Zone, Floor, Quadrant
int_group = temp_int.groupby(['ZONE', 'FLOOR', 'QUADRANT'])

'''
    Get Date Range of Interior Building Temperatures Desired
    Interpolate temperatures for timestamps with nan values
'''
def process_building_quadrant(group, group_data):
    start = find_15min_interval_after(group_data.ix[min_idx, 'TIMESTAMP'][:19])
    end = find_15min_interval_before(group_data.ix[max_idx, 'TIMESTAMP'][:19])
    date_range = pd.date_range(start, end, freq='15min')

    index = [dt.datetime.strptime(date_string[:19], date_fmt) for date_string in group_data.TIMESTAMP]
    group_data.index = index

    new_index_set = set(date_range) - set(index)
    new_index = pd.Series(sorted(list(new_index_set)))
    nan_df = pd.DataFrame(np.empty((len(new_index), len(group_data.columns))) * np.nan)
    nan_df.index = new_index
    nan_df.columns = group_data.columns

    merged_df = group_data.append(nan_df)
    merged_df = merged_df.ix[sorted(merged_df.index)]

    merged_df.VALUE = merged_df.VALUE.interpolate(method='time')
    merged_df.FLOOR, merged_df.QUADRANT = group
    #merged_df.ZONE, merged_df.FLOOR, merged_df.QUADRANT = group
    merged_df.TIMESTAMP = merged_df.index
    merged_df = merged_df.ix[date_range, :]
    return merged_df

df = pd.DataFrame()

for group, group_data in int_group:
    group_data = group_data.sort('TIMESTAMP')
    min_idx = group_data.index[0]
    max_idx = group_data.index[len(group_data)-1]
    #print group, group_data.ix[min_idx, 'TIMESTAMP'], group_data.ix[max_idx, 'TIMESTAMP']
    cleaned_group_data = process_building_quadrant(group, group_data)
    df = df.append(cleaned_group_data)

df.to_pickle('../interior_temps_df.p')
df.to_csv('../interior_temps.csv', index=False)

## HAVEN'T FIGURED OUT HOW TO "INTERPOLATE" THE EQUIPMENT NUMBER

# get nanrows
nan_rows = pd.isnull(merged_df).any(1).nonzero()[0]







'''
    Create a matrix of interior temperatures indexed by timestamps, columns are floor/quadrant pairs

'''


floors = temp_int.groupby(['FLOOR'])
quadrants = temp_int.groupby(['FLOOR', 'QUADRANT'])

date_fmt = '%Y-%m-%d %H:%M:%S'

start_ts_str = min(temp_int.TIMESTAMP)[:19]
end_ts_str = max(temp_int.TIMESTAMP)[:19]
start = dt.datetime.strptime(start_ts_str, date_fmt)
end = dt.datetime.strptime(end_ts_str, date_fmt)
date_range = pd.date_range(start, end, freq='15min')

groups = []
for group, group_data in quadrants:
    groups.append(group)
    print group

df2 = pd.DataFrame(index=date_range, columns=groups)

for idx, row in df.iterrows():
    quad = (row.FLOOR, row.QUADRANT)
    df2.ix[idx, quad] = row.VALUE
    print i, quad, row.VALUE

df2 = df2.ix[date_range]
df2.to_pickle('../interior_temps_mat.p')
df2.to_csv('../interior_temps_mat.csv')



'''
    Organizing Startup and Rampdown Times for each building
'''

startup_rampdown = pd.read_csv('Score_Startup_Rampdown.csv')
startup_rampdown['Building'] = startup_rampdown['Building'].apply(lambda x: x.split()[0])
startup_rampdown['Tag'] = startup_rampdown['Tag'].apply(lambda x: x.split()[0])

start_ramp_groups = startup_rampdown.groupby(['Tag'])
startup_data = start_ramp_groups.get_group('startup')
rampdown_data = start_ramp_groups.get_group('rampdown')

startup_buildings = startup_data.groupby('Building')
rampdown_buildings = rampdown_data.groupby('Building')

startup = {}
for building, building_data in startup_buildings:
    startup[building] = building_data.ix[:, ['Actual_DateTime', 'Comment']]

rampdown = {}
for building, building_data in rampdown_buildings:
    rampdown[building] = building_data.ix[:, ['Actual_DateTime', 'Comment']]


startup_345 = {}

interior_temps = pd.read_pickle('interior_temps_mat.p')

for startup_time in sorted(startup['345'].Actual_DateTime):
    day = dt.datetime.strptime(startup_time[:10], '%Y-%m-%d')
    day_range = pd.date_range(day, freq='15min', periods=96)
    startup_345[startup_time] = interior_temps.ix[day_range]
    print startup_time

pickle.dump(startup_345, open('../startup_345.p', 'wb'))



'''
    Plot Daily Quadrant/Floor Interior Temperatures 
'''

# Create time of day / hour value in float (e.g. 13.75 is 1:45 P.M.)
interior_temps['time_of_day'] = [x.hour + x.minute/60.0 for x in interior_temps.index]

interior_temps = pd.read_csv('../interior_temps_mat2.csv')

interior_temps['month'] = [x.date().month for x in interior_temps.index]
interior_temps['year'] = [x.date().year for x in interior_temps.index]
interior_temps['week'] = [x.isocalendar()[1] for x in interior_temps.index]
interior_temps['day_of_week'] = [x.weekday() for x in interior_temps.index]
interior_temps['weekend'] = [1 if x >= 5 else 0 for x in interior_temps.day_of_week]

day_of_week = {
                0: 'Monday',
                1: 'Tuesday', 
                2: 'Wednesday', 
                3: 'Thursday', 
                4: 'Friday',
                5: 'Saturday',
                6: 'Sunday', 
}
                

interior_temps.to_pickle('../interior_temps_mat2.p')
interior_temps.to_csv('../interior_temps_mat2.csv')

weekday_data = interior_temps.query('weekend==0')

weekly_group = weekday_data.groupby(['month', 'week'])

for week, weekly_data in weekly_group:
    quad_data = weekly_data[[quadrant, 'time_of_day']]
    plt.figure()
    plt.plot(quad_data['time_of_day'], quad_data)
    plt.title('week : ' + str(week))

plt.show()




for quadrant in interior_temps.columns[-1]:
    print quadrant

plt.figure()
plt.plot(interior_temps['time_of_day'], interior_temps[quadrant])    
plt.show()















