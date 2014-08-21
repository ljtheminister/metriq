import pyodbc
import datetime as dt
import numpy

class database:
    """
    class to initiate database connection.
    """
    def __init__(self, dsn, uid, pwd, database):
        """
        Constructor

        parameters
        ----------
        dsn: str
            data source name str.
        uid: str
            database user id.
        pwd: str
            database user pwd.
        database: str
            database name 
        """
        self.dsn = dsn
        self.uid = uid  
        self.pwd = pwd
        self.database = database
    
    def connect(self):
        """
        Create database connection

        return
        ------
        conn: object 
            database connection object
        """
        conn_str = ('DSN={0};UID={1};PWD={2};DATABASE={3}'.format(self.dsn,
            self.uid, self.pwd, self.database))
        conn = pyodbc.connect(conn_str)
        return conn

def timestamp_list(data):
    """
    Returns the list of available timestamps.

    parameters
    ----------
    data : list(str, list(datetime), list(float))
        A list of pointname, list of timestamps and list of float.

    Return
    ------
    timestamps: list(datetime)
        List of all timestamps in the dataset.
    """
    all_timestamps = set([])
    pointnames = []
    for [pointname, timestamps, values] in data:
        all_timestamps = all_timestamps.union(set(timestamps))
        pointnames.append(pointname)

    timestamps = sorted(list(all_timestamps))
    return timestamps

def building_data(base_time, bldg_tables, bldg_db_con):
    """
    Return bulding data.

    parameters
    ----------
    base_time: str
        A data string in 'yyyy-mm-dd' format. Only data produced after this
        date is returned.
    bldg_tables: list(str)
        List of building table names
    
    return
    ------
    unprocessed_dataset: list(list(str, list(datetime), list(float)))
        A list of lists where each list contains pointname, list of timestamp,
        and list of values.
    """
    #output dataset
    unprocessed_dataset = []

    ## get building data
    cursor = bldg_db_con.cursor()
    pointname_query_template = ("SELECT DISTINCT ZONE, FLOOR, QUADRANT, "
                                "EQUIPMENT_NO FROM [{0}] WHERE TIMESTAMP > "
                                "'{1}'")
    tableentry_query_template = ("SELECT TIMESTAMP, VALUE FROM [{0}] WHERE "
                                 "ZONE='{1}' AND FLOOR='{2}' AND "
                                 "QUADRANT='{3}' AND EQUIPMENT_NO='{4}' "
                                 "AND TIMESTAMP > '{5}' ORDER BY TIMESTAMP")

    for table in bldg_tables:
        query = pointname_query_template.format(table, base_time)
        cursor.execute(query)
        pointnames = cursor.fetchall()
        for p in pointnames:
            pointname = (table[:3] + str(p.ZONE) + str(p.FLOOR) +
                         str(p.QUADRANT) + table[12:27] + str(p.EQUIPMENT_NO) +
                         table[30:])
            query = tableentry_query_template.format(table, p.ZONE, p.FLOOR,
                                                    p.QUADRANT, p.EQUIPMENT_NO, 
                                                    base_time) 
            cursor.execute(query)
            entries = cursor.fetchall()
            print pointname + ": " + str(len(entries)) + " points"
            x = []
            y = []
            for e in entries:
                    x.append(e.TIMESTAMP)
                    y.append(e.VALUE)
            unprocessed_dataset.append([pointname, x, y])

    cursor.close()
    bldg_db_con.close()
    return unprocessed_dataset

def weather_data(base_time, weather_table, wea_db_con):
    """
    Return weather data.

    parameters
    ----------
    base_time: str
        A data string in 'yyyy-mm-dd' format. Only data produced after this
        date is returned.
    weather_table: list(str)
        Weather table name.
    
    return
    ------
    unprocessed_dataset: list(list(str, list(datetime), list(float)))
        A list of lists where each list contains pointname, list of timestamp,
        and list of values.
    """

    unprocessed_dataset = []
    ## get weather data
    cursor = wea_db_con.cursor()
    pointnames = ['TempA', 'Humidity']
    for p in pointnames:
        query = ("SELECT Date, {0} FROM [{1}] WHERE Date > '{2}' ORDER"
                 " BY Date") 
        query = query.format(p, weather_table, base_time)
        cursor.execute(query)
        entries = cursor.fetchall()
        print p + ": " + str(len(entries)) + " points"
        x = []
        y = []
        for e in entries:
            x.append(dt.datetime.strptime(e[0][:-1],
                "%Y-%m-%d %H:%M:%S.%f"))
            y.append(e[1])
        unprocessed_dataset.append([weather_table + '_' + p, x, y])
    cursor.close()
    wea_db_con.close()

    return unprocessed_dataset

def interpolate_data(all_timestamps, unprocessed_dataset, granularity):
    """
    Finds the values for the all the pointnames at all_timestamps. Linearly
    interpolates data if it is not available for a timestamp. 

    parameters
    ----------
    all_timestamps: list(datetime)
        List of timestamps.
    unprocessed_dataset: list(list(str, list(timestamp), list(float)))
        List of data for all point names.

    return
    ------
    X: numpy.matrix
        Interpolated observation matrix.
    pointnames: list(str)
        List of pointnames.  
    timestamps: list(datetime)
        List of timestamps.
    """
    ud = unprocessed_dataset
    pointnames = []
    for [pointname, timestamps, values] in ud:
        pointnames.append(pointname)

    base = min(all_timestamps)
    end = max(all_timestamps)
    timestamps = []
    timestamps_offset = []
    current = base
    current_offset = 0
    while current <= end:
        timestamps.append(current)
        timestamps_offset.append(current_offset)
        current += dt.timedelta(0, granularity * 60)
        current_offset += granularity

    matrix = []
    for [pointname, ts, values] in ud:
        x = []
        for t in ts:
            offset = t-base
            x.append(offset.days * 24 * 60 + offset.seconds / 60)
        interpolated_values = numpy.interp(timestamps_offset, x, values)
        matrix.append(list(interpolated_values))

    matrix = numpy.matrix(matrix)
    matrix = numpy.asarray(matrix)
    X = matrix.transpose()
    X = numpy.asarray(X)

    return X, pointnames, timestamps

def csv(X, pointnames, timestamps, file_path):
    """
    Write the dataset into csv files. The rows correspond to the timestamps and
    the columns to pointnames.

    parameters
    ----------
    X: numpy.matrix
        Matrix with observation vectors stacked along axis 1.
    pointnames: list(str) 
        names representing the measurements. 
    timestamps: list(str)
        list of timestamp strings when the measurements were made.  
    filepath: str
        csv filepath to write the data to.
    """
    File = open(file_path, 'w')
    File.write("Timestamp, ")
    for i in range(0, len(pointnames)-1):
        File.write(pointnames[i] + ", ")
    File.write(pointnames[-1] + '\n')

    for i in range(0, len(X)):
        File.write(str(timestamps[i]) + ", ")
        for j in range(0, len(X[i])-1):
                File.write(str(X[i][j]) + ", ")
        File.write(str(X[i][-1]) + '\n')


if __name__ == '__main__':
    # fetch building data
    bldg_db_conn = database('anderson', 'tpo', 'tpo', '345').connect()  
    bldg_tables = ["345---------001BMSELEMET------VAL001",
              "345---------001BMSSTEMET------VAL001",
              "345---------001BMSHVAFANRAT---VAL001",
              "345---------001BMSHVAFANRHC---VAL001",
              "345---------001BMSHVAFANSAT---VAL001",
              "345---------001BMSHVATEMPSP---VAL001",
              "345---------001BMSHVATEMSPA---VAL001"]
    base_time = '2014-07-01'
    bldg_data = building_data(base_time, bldg_tables, bldg_db_conn)

    timestamps = timestamp_list(bldg_data)
    # fetch weather observations history
    wea_table = 'Observations_History'
    wea_db_conn = database('anderson', 'tpo', 'tpo', 'Weather').connect()  
    wea_observation_data = weather_data(base_time, wea_table, wea_db_conn) 

    # fetch weather forecast history
    wea_table = 'Hourly_Forecast'
    wea_db_conn = database('anderson', 'tpo', 'tpo', 'Weather').connect()  
    wea_forecast_data = weather_data(base_time, wea_table, wea_db_conn) 

    data = bldg_data + wea_forecast_data + wea_observation_data
    X, pointnames, timestamps = interpolate_data(timestamps, data, 15)
    csv(X, pointnames, timestamps, 'snapshot.csv')

