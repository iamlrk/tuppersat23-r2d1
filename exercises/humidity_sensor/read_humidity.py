# import board
# import busio
from machine import I2C
import hum
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
devices = i2c.scan()

if devices:
    for d in devices:
        print(hex(d))
        
# I2C address
SHT31D_ADDR = 0x44
