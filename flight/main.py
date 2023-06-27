from tuppersat.r2d1 import R2D1

# sensor imports 
from code.sensors.pressure import Pressure
from code.sensors.temperature import Temperature
from code.sensors.uv import UV
from code.sensors.humidity import Humidity
from code.sensors.sdcard import SDCard

# gps imports
from code.gps.gps import GPS

grouped_sensors = {
    'data'      : {
        'sensors' : [UV(), Humidity(), GPS()],
        'store_length': 4,
        'specified_format': 'R2D1',
        'transmit_time': 24
        },
    'telemetry' : {
        'sensors' : [Temperature(), Pressure(), GPS()],
        'store_length': 1,
        'specified_format': 'UCD',
        'transmit_time': 20
        },
    'storage'   : {
        'sensors' : [SDCard()],
        'store': False
        },
}
r2d1 = R2D1(**grouped_sensors)
r2d1.start()