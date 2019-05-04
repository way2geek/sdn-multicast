import time
import datetime
i=0

while i<90:
    ts=time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print st
    time.sleep(3)
    i=i+1
