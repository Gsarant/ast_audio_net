from datetime import datetime,timedelta

def get_date_after(dt_date,days=30):
    dt_delta = timedelta(days=days)
    new_date=(dt_date + dt_delta)
    new_date=new_date.replace(hour=23, minute=59, second=59,microsecond=999)
    return new_date

def get_date_before(dt_date,days=30):
    dt_delta = timedelta(days=days)
    new_date=(dt_date - dt_delta)
    new_date=new_date.replace(hour=0, minute=0, second=0,microsecond=0)
    return new_date

def get_date_00(str_date,format='%Y-%m-%d %H:%M:%S'):
    old_date=str_to_date(str_date,format)
    new_date=old_date.replace(hour=0, minute=0, second=0,microsecond=0)
    return new_date

def get_date_99(str_date,format='%Y-%m-%d %H:%M:%S'):
    old_date=str_to_date(str_date,format)
    new_date=old_date.replace(hour=23, minute=59, second=59,microsecond=999)
    return new_date

def str_to_date(str_date,format='%Y-%m-%d %H:%M:%S'):
    str_date=str_date.replace('T',' ')
    pos_=str_date.find(':')
    if pos_== -1:
        return datetime.strptime(str_date,format[0:8])
        
    return datetime.strptime(str_date,format)

def date_to_str(dt_date,format='%Y-%m-%d %H:%M:%S'):

    return dt_date.strftime(format)

def get_now_str():
    str_date=date_to_str(datetime.now())
    return str_date

def get_now_date():
    return datetime.now()


    
    