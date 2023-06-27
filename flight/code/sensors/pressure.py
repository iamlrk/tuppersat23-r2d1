import machine
import time

# GLOBAL
SENSOR_ADDRESS = 0x77


class Pressure:
    """This is a class to interface with the MS5611-01BA03 Barometric Pressure Sensor 
        
        Args:
        bus (int, optional): The I2C Bus the sensor is connected to. Defaults to 0.
        sensor_address (hexadecimal, optional): The sensor adddress - MS5611-01BA03 Defaults to 0x77.
        sda (int, optional): SDA Pin Nummber. Defaults to 0.
        scl (int, optional): SCL Pin Number. Defaults to 1.
        freq (int, optional): Frequency. Defaults to 400000.
    """

    def __init__(self, bus=0, sensor_address=0x77, sda=0, scl=1, freq=400000):
        """_summary_
        """
        self.coefficients = {}
        self.sensor_status = None
        self.i2c = None
        self.bus = bus
        self.sensor_address = sensor_address
        self.sda = sda
        self.scl = scl
        self.freq = freq
        self.D1, self.D2, self.temp, self.dT, self.off, self.sens = 0, 0, 0, 0, 0, 0

    def get_coefficients(self):
        """Stores the orrection coefficients for the connectedd sensors
        """
        value_coefficients = []
        for i in range(8):
            self.i2c.writeto(self.sensor_address, bytes([0xA0 + i * 2]))
            data = self.i2c.readfrom(self.sensor_address, 2)
            value_coefficients.append(int.from_bytes(data, 'big'))

        for i in range(len(value_coefficients)):
            self.coefficients['C' + str(i)] = value_coefficients[i]

    def setup(self):
        """Sets the sensor up and creates a i2c variable. 
        If not available then sensor status_vaiable is False
        """
        try:
            self.sensor_status = True
            self.i2c = machine.I2C(self.bus, sda=machine.Pin(self.sda), scl=machine.Pin(self.scl), freq=self.freq)
            self.get_coefficients()
        except Exception as e:
            # TODO: write default conditions
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > SETUP > PRESSURE > {e}\n')
            self.sensor_status = False

    def get_raw_data(self):

        # CALL PRESSURE
        # Send command to start pressure conversion with oversampling rate of 4096 (OSR=4096)
        self.i2c.writeto(self.sensor_address, bytes([0x48]))
        # Wait for pressure conversion to finish (9.04 ms for OSR=4096)
        time.sleep_ms(10)
        # Send command to read ADC result 
        self.i2c.writeto(self.sensor_address, bytes([0x00]))
        # Read three bytes of data 
        data = self.i2c.readfrom(self.sensor_address, 3)
        # Convert data to integer value 
        value = int.from_bytes(data, 'big')
        # define pressure
        self.D1 = value  # Raw pressure value

        # CALL TEMPERATURE
        # Send command to start temperature conversion with oversampling rate of 4096 (OSR=4096)
        self.i2c.writeto(self.sensor_address, bytes([0x58]))
        # Wait for temperature conversion to finish (9.04 ms for OSR=4096)
        time.sleep_ms(10)
        # Send command to read ADC result 
        self.i2c.writeto(self.sensor_address, bytes([0x00]))
        # Read three bytes of data 
        data = self.i2c.readfrom(self.sensor_address, 3)
        # Convert data to integer value 
        value = int.from_bytes(data, 'big')
        # define temperature
        self.D2 = value  # Raw temperature value

    def convert_readings(self):
        """ Need to update based on the other i2c comms"""
        # Calculate difference between actual and reference temp11erature 
        self.dT = self.D2 - self.coefficients['C5'] * pow(2, 8)
        self.temp = 2000 + ((self.dT * self.coefficients['C6']) / pow(2, 23))

        # Calculate offset at actual temperature
        self.off = self.coefficients['C2'] * pow(2, 16) + ((self.coefficients['C4'] * self.dT) / pow(2, 7))
        # Calculate sensitivity at actual temperature 
        self.sens = self.coefficients['C1'] * pow(2, 15) + ((self.coefficients['C3'] * self.dT) / pow(2, 8))

        if self.temp < 2000:
            _t_corr = pow(self.dT, 2) / pow(2, 31)
            _off_corr = 5 * pow((self.temp - 2000), 2) / 2
            _sensor_corr = (29 * pow((self.temp - 2000), 2)) / 2
            if self.temp < -1500:
                _off_corr = _off_corr + 7 * pow((self.temp + 1500), 2)
                _sensor_corr = _sensor_corr + 11 * pow((self.temp + 1500), 2) / 2

        else:
            _t_corr = _off_corr = _sensor_corr = 0

        temperature_final = self.temp - _t_corr
        self.off -= _off_corr
        self.sens -= _sensor_corr

        return (self.D1 * self.sens / pow(2, 21) - self.off) / pow(2, 15), temperature_final

    def read(self):
        """Reads the raw data from the sensor and corrects the values if the self.sensor_status is True. 
        If self.sensor_status is False then it returns 99999999

        Returns:
            float, float: pressure, temperature
        """
        try:
            self.get_raw_data()
            # self.get_correcting_factors()
            pressure, temperature = self.convert_readings()
            # time = time.time() 
            return {'pressure' :pressure, 'temperature': temperature}
        except Exception as e:
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > READ > PRESSURE > {e}\n')
            return {'pressure' :101, 'temperature': 101}


def main():
    pressure = Pressure()
    pressure.setup()
    while True:
        print(pressure.read())
        time.sleep(1)
    return


if __name__ == '__main__':
    main()
