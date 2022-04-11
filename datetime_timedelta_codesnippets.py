
# Timedelta function demonstration

from datetime import datetime, timedelta, date
import time
import calendar

try:
    a = datetime(2021, 6, 31)
    b =a  + timedelta(days = -1)


    c = tuple(b.timetuple()[:3])
except:
    c = (0,0,0)


print (c)


#https://www.saltycrane.com/blog/2008/11/python-datetime-time-conversions/
#-------------------------------------------------
# conversions to strings
#-------------------------------------------------
# datetime object to string
dt_obj = datetime(2008, 11, 10, 17, 53, 59)
date_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
print (date_str)

# time tuple to string
time_tuple = (2008, 11, 12, 13, 51, 18, 2, 317, 0)
date_str = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)
print (date_str)

#-------------------------------------------------
# conversions to datetime objects
#-------------------------------------------------
# time tuple to datetime object
time_tuple = (2008, 11, 12, 13, 51, 18, 2, 317, 0)
dt_obj = datetime(*time_tuple[0:6])
print (repr(dt_obj))
# date string to datetime object
date_str = "2008-11-10 17:53:59"
dt_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
print (repr(dt_obj))

# timestamp to datetime object in local time
timestamp = 1226527167.595983
dt_obj = datetime.fromtimestamp(timestamp)
print (repr(dt_obj))

# timestamp to datetime object in UTC
timestamp = 1226527167.595983
dt_obj = datetime.utcfromtimestamp(timestamp)
print (repr(dt_obj))

#-------------------------------------------------
# conversions to time tuples
#-------------------------------------------------
# datetime object to time tuple
dt_obj = datetime(2008, 11, 10, 17, 53, 59)
time_tuple = dt_obj.timetuple()
print (repr(time_tuple))

# string to time tuple
date_str = "2008-11-10 17:53:59"
time_tuple = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
print (repr(time_tuple))

# timestamp to time tuple in UTC
timestamp = 1226527167.595983
time_tuple = time.gmtime(timestamp)
print (repr(time_tuple))

# timestamp to time tuple in local time
timestamp = 1226527167.595983
time_tuple = time.localtime(timestamp)
print (repr(time_tuple))

#-------------------------------------------------
# conversions to timestamps
#-------------------------------------------------
# time tuple in local time to timestamp
time_tuple = (2008, 11, 12, 13, 59, 27, 2, 317, 0)
timestamp = time.mktime(time_tuple)
print (repr(timestamp))

# time tuple in utc time to timestamp
time_tuple_utc = (2008, 11, 12, 13, 59, 27, 2, 317, 0)
timestamp_utc = calendar.timegm(time_tuple_utc)
print (repr(timestamp_utc))


# Convert the date to a period date type:
# https://stackoverflow.com/a/68448209/4173718
pat = r"(?P<Q>.)(?P<quarter>\d+)\.(?P<year>.+)"
repl = lambda m: f"{m.group('quarter')}{m.group('Q')}20{m.group('year')}"
df = df.assign(date = df.date
                       .str.replace(pat, repl, regex=True)
                       .transform(pd.Period)
               )

#-------------------------------------------------
# results
#-------------------------------------------------
# 2008-11-10 17:53:59
# 2008-11-12 13:51:18
# datetime.datetime(2008, 11, 12, 13, 51, 18)
# datetime.datetime(2008, 11, 10, 17, 53, 59)
# datetime.datetime(2008, 11, 12, 13, 59, 27, 595983)
# datetime.datetime(2008, 11, 12, 21, 59, 27, 595983)
# (2008, 11, 10, 17, 53, 59, 0, 315, -1)
# (2008, 11, 10, 17, 53, 59, 0, 315, -1)
# (2008, 11, 12, 21, 59, 27, 2, 317, 0)
# (2008, 11, 12, 13, 59, 27, 2, 317, 0)
# 1226527167.0
# 1226498367