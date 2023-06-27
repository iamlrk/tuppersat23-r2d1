import time

def time_since_epoch(epoch):
    return (time.ticks_ms() - epoch)/1000