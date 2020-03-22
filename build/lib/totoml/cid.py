import datetime
from random import randint

def cid(): 
    '''
    Generates a Toto-valid Correlation ID
    Example: 20200229160021694-09776
    '''
    datepart = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    randpart = str(randint(0, 100000)).zfill(5)

    return '{date}-{rand}'.format(date=datepart, rand=randpart)
