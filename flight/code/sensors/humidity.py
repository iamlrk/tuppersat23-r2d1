from machine import I2C, Pin
import time

R_HIGH = const(1)
R_MEDIUM = const(2)
R_LOW = const(3)


class Humidity():
    """
    This class implements an interface to the SHT31 temperature and humidity
    sensor from Session.
    """

    # This static map helps keeping the heap and program logic cleaner
    _map_cs_r = {
        True: {
            R_HIGH: b'\x2c\x06',
            R_MEDIUM: b'\x2c\x0d',
            R_LOW: b'\x2c\x10'
        },
        False: {
            R_HIGH: b'\x24\x00',
            R_MEDIUM: b'\x24\x0b',
            R_LOW: b'\x24\x16'
        }
    }

    def __init__(self, bus=0, sda=Pin(0), scl=Pin(1), addr=0x44, freq=400000):
        """
        Initialize a sensor object on the given I2C bus and accessed by the
        given address.
        Args:
            bus (int, optional): I2C bus number. Defaults to 0.
            sda (Pin, optional): Pin object for SDA. Defaults to Pin(0).
            scl (Pin, optional): Pin object for SCL. Defaults to Pin(1).
            addr (int, optional): I2C address of the sensor. Defaults to 0x44.
            freq (int, optional): I2C clock frequency in Hz. Defaults to 400000.
        """
        # if i2c == None:
        #    raise ValueError('I2C object needed as argument!')
        # self._i2c = i2c
        self._i2c = None
        self._addr = addr
        self.bus = bus
        self.sda = sda
        self.scl = scl
        self.freq = freq

    def setup(self):
        """
        Initializes the I2C interface with the sensor.
        """
        try:
            self._i2c = I2C(self.bus, scl=self.scl, sda=self.sda, freq=400000)
        except:
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > SETUP > HUMIDITY > {e}\n')

    def _send(self, buf):
        """
        Sends the given buffer object over I2C to the sensor.
        """
        self._i2c.writeto(self._addr, buf)

    def _recv(self, count):
        """
        Read bytes from the sensor using I2C. The byte count can be specified
        as an argument.
        Returns a bytearray for the result.
        """
        return self._i2c.readfrom(self._addr, count)

    def _raw_temp_humi(self, r=R_HIGH, cs=True):
        """
        Read the raw temperature and humidity from the sensor and skips CRC
        checking.
        Returns a tuple for both values in that order.
        """
        if r not in (R_HIGH, R_MEDIUM, R_LOW):
            raise ValueError('Wrong repeatability value given!')
        self._send(self._map_cs_r[cs][r])
        time.sleep_ms(50)
        raw = self._recv(6)
        return (raw[0] << 8) + raw[1], (raw[3] << 8) + raw[4]

    def read(self, resolution=R_HIGH, clock_stretch=True, celsius=True):
        """
        Reads the temperature and humidity values from the sensor.

        Args:
            resolution (int, optional): The repeatability setting. Defaults to R_HIGH.
            clock_stretch (bool, optional): The clock stretching setting. Defaults to True.
            celsius (bool, optional): Whether to return the temperature value in Celsius or Fahrenheit. Defaults to True.

        Returns:
            dict: A dictionary containing the temperature and humidity values.
        """
        try:
            t, h = self._raw_temp_humi(resolution, clock_stretch)
            return {'humidity' :self._raw_temp_humi(resolution, clock_stretch)[1], 'temperature' :self._raw_temp_humi(resolution, clock_stretch)[0]}
        except Exception as e:
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > READ > HUMIDITY > {e}\n')
            return {'humidity' :101, 'temperature' :101}

def main():
    humidity = Humidity()
    humidity.setup()
    return humidity.read()


if __name__ == '__main__':
    while True:
        print(main())
        time.sleep(1)

