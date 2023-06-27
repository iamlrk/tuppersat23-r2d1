from machine import Pin, UART, SoftI2C
import utime, time
from code.gps.airborne import set_airborne_mode

class GPS(): 
    def __init__(self, bus = 0, baudrate = 9600, tx = Pin(12), rx = Pin(13), timeout = 10, timeout_char = 10): 
        self.bus = bus 
        self.baudrate = 9600
        self.tx = tx
        self.rx = rx
        self.timeout = timeout
        self.timeout_char = timeout_char
         
    def setup(self):
        self.gpsModule = UART(self.bus, self.baudrate, tx = self.tx, rx=self.rx, timeout = self.timeout, timeout_char = self.timeout_char)
        set_airborne_mode(self.gpsModule)
        
    def read_string(self):
        
        timeout_start = time.time()
        timeout_loop = 2
        self.gps_list = []
        
        while time.time() < timeout_start + timeout_loop:
            #print(time.time())
            #print(timeout_start + timeout_loop)
            #print('-'*50)
            telemetry = self.gpsModule.readline()
            # print(telemetry)
            if telemetry:
                # print(telemetry)
                try:
                    gps_line = telemetry.decode()
                    # print(gps_line)
                    gps_line = gps_line.split(',')
                    
                    if gps_line[0] == '$GPGGA' and len(gps_line) == 15:
                        self.gps_list.append(gps_line)
                        
                except:
                    continue
                    
    def get_decimal_degree(self, dddmm_mm):
        try:
            if len(dddmm_mm) == 12: 
                ddd = float(dddmm_mm[0:3])
                mm_mm = float(dddmm_mm[3:-2])/60
            else: 
                ddd = float(dddmm_mm[0:2])
                mm_mm = float(dddmm_mm[2:-2])/60
            if dddmm_mm[-1] == 'N' or dddmm_mm[-1] == 'E': 
                return ddd+mm_mm
            else: 
                return -(ddd+mm_mm)
        except Exception as e:
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > GPS > {e}\n')
            return 11122.00
            
        

    
    def build_dictionary(self):
        self.read_string()
        # print(self.gps_list)
        if self.gps_list:
            dic = {'hhmmss': [j[1] for j in self.gps_list][-1],
                   'latitude': [self.get_decimal_degree(j[2]+j[3]) for j in self.gps_list][-1],
                   'longitude': [self.get_decimal_degree(j[4]+j[5]) for j in self.gps_list][-1],
                   'altitude': [j[9] for j in self.gps_list][-1],
                   'hdop': [j[11] for j in self.gps_list][-1]}
        else:
            dic = None
        return dic 
            
    def read(self):
        dic = self.build_dictionary()
        # print(dic)
        if not dic:
            return {
                'hhmmss': '131424.00',
                'longitude': -1133.778,
                'latitude': 1133.778,
                'altitude': 11111,
                'hdop': 13.5,
                }
        elif dic.get('hdop'):
            return dic
        else:
            return {
                'hhmmss': '131424.00',
                'longitude': -1133.778,
                'latitude': 1133.778,
                'altitude': 11111,
                'hdop': 13.5,
                }

def main():
    gps = GPS()
    gps.setup()
    while True:
        print(gps.read())


if __name__ == '__main__':
    main()