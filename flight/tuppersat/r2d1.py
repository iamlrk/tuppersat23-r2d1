# uPython imports
from machine import UART, Pin, Timer

# tuppersat imports
# radio imports
from tuppersat.radio import TupperSatRadio

# sensor imports 
from code.sensors.pressure import Pressure
from code.sensors.temperature import Temperature
from code.sensors.uv import UV
from code.sensors.humidity import Humidity
from code.sensors.sdcard import SDCard

# communication imports
from code.comms.write_to_csv import CSV
from code.comms.radio import Radio
from code.comms.packets import package_it, put_in_dict, generated_to_required
from code.comms.write_to_files import MultiFileWriter
from code.comms.time_keeper import time_since_epoch
from code.comms.transmit import transmit as trans

# gps imports
from code.gps.gps import GPS

# standard library imports
from collections import namedtuple
import time


class R2D1():
    def __init__(self, **grouped_sensors) -> None:
        self.grouped_sensors = grouped_sensors
        self.generated_packets = {}
        self.generated_named_tuple = {}
        self.filenames = {}
        self.cached_data_length = 0
        self.send_packets = {}
        self.write_packets = {}
        self.send_this = {}
        self.led = Pin(25, Pin.OUT)
        self.epoch = time.ticks_ms()
        self.last_transmit = {}
        self.mem_packets = {}
        self.packet_count = {}
        self.packet_rate = {}
        self.write_packets = {}
        self.store_count = {}
        self.organised_packets = {}
        self.useful_packets = {} # these packs have atleast 1 telemetry packet or 4 data packets
        self.log_method = print 

    def setup(self):
        with open('data/logs.log', 'a') as self.logging:
            self.logging.write(f'------Mission Start------\n')
            self.logging.write(f'Start Time - {self.epoch}\n')
            for group, sensors_info in self.grouped_sensors.items():
                if sensors_info.get('store', True):
                    self.filenames[group] = f'/data/{group}.csv'
                # self.filenames.append(f'/data/{group}.txt')
                setups = [sensor.setup() for sensor in sensors_info.get('sensors')]
                self.logging.write(f"{self.time_since_epoch():9} > SETUP    > {group.upper():9} > {', '.join([str(sensor).split()[0][1:] for sensor in sensors_info.get('sensors')])}\n")
            self.radio = Radio().setup()
            self.logging.write(f"{self.time_since_epoch():9} > SETUP    > Radio\n")
            self.init_packet()
            self.logging.write(f"{self.time_since_epoch():9} > SETUP    > Created empty packets\n")
            
    def init_packet(self):
        for group, sensors_info in self.grouped_sensors.items():
            if not sensors_info.get('store', True):
                del self.grouped_sensors[group]
                break
            sensor_group = ['hhmmss'] + [str(sensor).split()[0][1:].lower() for sensor in sensors_info.get('sensors')]
            self.generated_named_tuple[group] = namedtuple(group, sensor_group)
            self.packet_count[group] = 1
            self.packet_rate[group] = 1
            self.generated_packets[group] = []
            self.organised_packets[group] = []
            self.useful_packets[group] = []
            self.store_count[group] = 0
            self.write_packets[group] = None
            self.mem_packets[group] = None
            self.last_transmit[group] = self.time_since_epoch()
        #todo make this dynamic
        # self.last_transmit['data'] = self.time_since_epoch() + self.transmit_time / 2
        # self.last_transmit['telemetry'] = self.time_since_epoch()
    
    def time_since_epoch(self):
        return time_since_epoch(self.epoch)
    
    def blink(timer):
        led.toggle()
    
    def log_info(self, message):
        self.log_method(message)
      
    def read(self):
        for group, sensors_info in self.grouped_sensors.items():
            # self.generated_packets.get(group).time = (time.time()) #TODO change this to ticks
            _read_from_sensor = [self.time_since_epoch()] + [sensor.read() for sensor in sensors_info.get('sensors')] # read 'read' as read and not read
            # for sensor in sensors_info.get('sensors'):
            self.generated_packets[group] = (self.generated_named_tuple[group](*_read_from_sensor))
            
            # self.generated_packets[group].append(self.generated_tuple[group](*_read_from_sensor))
    
    def change_dict_format(self):
        for group, group_info in self.grouped_sensors.items():
            self.organised_packets[group].append(generated_to_required(self.time_since_epoch(),
                                                                       group, self.generated_packets.get(group),
                                                                       group_info.get('specified_format', None)))
            self.write_packets[group] = package_it(self.time_since_epoch(), group, self.generated_packets.get(group))
            # print(self.write_packets)
    
    def check_length(self):
        for group, group_info in self.grouped_sensors.items():
            if len(self.organised_packets[group]) >= group_info.get('store_length', 1):
                self.useful_packets[group] = self.organised_packets.get(group)
                self.organised_packets[group] = []
        return
    
    def dict_to_packet(self):
        for group, group_info in self.grouped_sensors.items():
            if len(self.useful_packets.get(group)) == group_info.get('store_length', 1):
                self.send_packets[group] = put_in_dict(group, self.useful_packets.get(group))
                # self.write_packets[group] = package_it(self.time_since_epoch(), group, self.useful_packets.get(group))
                 # todo look for th bug
        
    def store(self):
     # need to look for an alternate method
        with open('data/logs.log', 'a') as logs:
            for group, group_info in self.grouped_sensors.items():
                self.files.get(group).write(f'{self.store_count.get(group)},{self.write_packets.get(group)}\n')
                logs.write(f'{self.time_since_epoch():9} > STORE    > {group.upper()}\n')
                self.store_count[group] += 1
        self.led.toggle()
        self.led.toggle()
        self.led.toggle()
    
    def transmit(self):
        with open('data/logs.log', 'a') as logs:
            for group, group_info in self.grouped_sensors.items():
                if - self.last_transmit.get(group) + self.time_since_epoch() >= group_info.get('transmit_time'):
                    trans(self.radio, self.time_since_epoch(),
                                  group,
                                  self.send_packets.get(group, 'EMPTY'),
                                  logs.write,
                                  self.packet_count.get(group),
                                  self.packet_rate.get(group),
                                  )
                    #print(f'{self.time_since_epoch():9} > TRANSMIT > {group.upper():9} > Packet Count - {self.packet_count.get(group)} > Packet Rate - {self.packet_rate.get(group)}\n')
                    self.packet_count[group] += 1
                    self.packet_rate[group] = self.packet_count.get(group)/((self.time_since_epoch())/60)
                    self.last_transmit[group] = self.time_since_epoch()
                    self.led.toggle()
    
    def sequence(self):
        # for writing
        self.read()
        self.change_dict_format()
        self.store()
        self.dict_to_packet()
        self.check_length()
        
        # print(self.send_packets)
        self.transmit()
        # self.log_info((self.write_packets.get('data')))
        # self.check_record_and_send()
    
    def start(self):
        self.setup()
        while True:
            with MultiFileWriter(self.filenames.values()) as self.files:
                self.sequence()
                
                            
def main():   
    grouped_sensors = {
        'data'      : {'sensors' : [UV(), Humidity(), GPS()], 'store_length': 4, 'specified_format': 'R2D1', 'transmit_time': 24},
        'telemetry' : {'sensors' : [Temperature(), Pressure(), GPS()], 'store_length': 1, 'specified_format': 'UCD', 'transmit_time': 20},
        'storage'   : {'sensors' : [SDCard()], 'store': False},
    }
    r2d1 = R2D1(**grouped_sensors)
    r2d1.start()

if __name__ == '__main__':
    main()