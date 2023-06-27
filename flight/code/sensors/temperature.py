import machine
import onewire
import ds18x20
import time


class Temperature():
    """
    This class implements an interface to the internal and external temperature sensor 
    """

    def __init__(self, pin=17):
        """
        Constructor method for the Temperature class.

        Args:
        - pin (int): An integer representing the GPIO pin number used for the one-wire interface. Default value is 17.

        Returns:
        - None: This method does not return anything.
        """
        self.all_sensors = None
        self.devices = None
        self.pin = pin

    def setup(self):
        """
        Sets up the one-wire interface to communicate with the temperature sensor.

        Args:
        - None

        Returns:
        - None: This method does not return anything.

        Raises:
        - If the one-wire interface is not found, an error message is printed.
        """
        try:
            all_pin = machine.Pin(self.pin)  # pin number on Pi Pico
            self.all_sensors = ds18x20.DS18X20(onewire.OneWire(all_pin))  # oneWire call
            self.find_devices()
        except Exception as e:
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > Temperature > OneWire Not Found > {e}')
        # print(self.devices)

    def find_devices(self):
        """returns the devices connected to the pi pico onewire setup"""
        self.devices = self.all_sensors.scan()
        # return all_sensors.scan(), all_sensors

    def get_temperature(self):
        """Returns the temperature values"""

        self.all_sensors.convert_temp()  # gets temp from sensor 
        if self.devices != []:
            return [self.all_sensors.read_temp(device) for device in self.devices]
        else:
             return [101, 101]

    def read(self):
        try:
            return {'temperature': self.get_temperature()}
        except Exception as e:
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > TEMPERATURE > 0 Sensors Connected > {e}\n')
            return {'temperature': [101, 101]}

def main():
    temp = Temperature()
    temp.setup()
    return temp.read()


if __name__ == '__main__':
    while True:
        print(main())
        time.sleep(1)
