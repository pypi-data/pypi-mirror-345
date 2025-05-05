import datetime as datetime_

timedelta = datetime_.timedelta
now = datetime_.datetime.now
utcnow = datetime_.datetime.utcnow
# return timestamp + utcoffset
fromtimestamp = datetime_.datetime.fromtimestamp
utcfromtimestamp = datetime_.datetime.utcfromtimestamp
timestamp = datetime_.datetime.timestamp
fromisoformat = datetime_.datetime.fromisoformat

del datetime_

def localtime(hours=8):
    utc_time = utcnow()
    time_delta = timedelta(hours=hours)
    my_time = utc_time + time_delta
    return my_time
