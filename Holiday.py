##### NEED TO CHECK DAYS AROUND THE HOLIDAYS WHETHER THEY BE THURSDAYS!!!
import pandas as pd, numpy as np, datetime as dt

class Holiday:
    def __init__(self, nature, sat_adj, sun_adj):


'''
    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate
        self.HolidayList = filterList(generateHolidays(self))
'''

    def generateHolidays(self):
        HolidayList = []
        startYear = self.startDate.year()
        endYear = self.endDate.year()

        for year in xrange(startYear, endYear+1):
            
        # New Year's:  Jan 1st
        # MLK: 3rd Monday in January
        # Inauguration Day:  January 20, every 4 years, starting in 1937
        # Washington's bday = third monday in February
        # Memorial Day: last monday in May
        # Flag Day?? June 14th
        # July 4th
        # Labor Day: first Monday in September
        # Columbus Day: second Monday in October
        # Election Day: Tuesday on or after Nov 2
        # Veterans Day:  Nov 11
        # Thanksgiving:  fourth Thursday in November
        # Christmas:  Dec 25
            return HolidayList


    def filterList(self):





    def addNewYear(year):
        return dt.date(year, 1, 1)

    def addMLK(year):

    def addInauguration(year):
    def addJuly4(year):
        return dt.date(year, 7, 4)
    
    def addLabor(year):
    def addColumbus(year):
    def addElection(year):
    def addVeterans(year):
    def addThanksgiving(year):
    def addChristmas(year):
        return dt.date(year, 12, 25)


