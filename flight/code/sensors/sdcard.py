from code.sensors.micro_sdcard import MicroSDCard
# from micro_sdcard import MicroSDCard
from machine import Pin, SPI
import uos
import time
from code.comms.write_to_csv import CSV


class SDCard:

    def __init__(self, pin_number=9, baudrate=1000000,
                 polarity=0,
                 phase=0,
                 bits=8,
                 firstbit=SPI.MSB,
                 sck=10,
                 mosi=11,
                 miso=8,
                 data_addr=None):
        """
        Initializes the SDCard object with the specified parameters.

        Args:
            pin_number (int): The pin number for the chip select (CS) pin. Default is 9.
            baudrate (int): The SPI baud rate. Default is 1000000.
            polarity (int): The SPI clock polarity. Default is 0.
            phase (int): The SPI clock phase. Default is 0.
            bits (int): The number of bits per SPI transfer. Default is 8.
            firstbit (int): The bit order for SPI transfers. Default is SPI.MSB.
            sck (int): The pin number for the SPI clock (SCK). Default is 10.
            mosi (int): The pin number for the SPI Master-Out-Slave-In (MOSI) line. Default is 11.
            miso (int): The pin number for the SPI Master-In-Slave-Out (MISO) line. Default is 8.
            data_addr (str): The directory where the data will be stored. Default is '/data'.
        """
        if not data_addr:
            data_addr = '/data'
        self.pin_number = pin_number
        self.baudrate = baudrate
        self.polarity = polarity
        self.phase = phase
        self.bits = bits
        self.firstbit = firstbit
        self.sck = sck
        self.mosi = mosi
        self.miso = miso
        self.data_addr = data_addr
        self.status = None

    def setup(self):
        """
        Initializes the SD card, mounts the file system, and returns a list of packet dictionaries.

        Returns:
            dict: A dictionary containing packet dictionaries.
        """
        try:
            # Assign chip select (CS) pin (and start it high)
            cs = Pin(self.pin_number, Pin.OUT)

            # Initialize SPI peripheral (start with 1 MHz)
            spi = SPI(1,
                      baudrate=self.baudrate,
                      polarity=self.polarity,
                      phase=self.phase,
                      bits=self.bits,
                      firstbit=SPI.MSB,
                      sck=Pin(self.sck),
                      mosi=Pin(self.mosi),
                      miso=Pin(self.miso))

            # Initialize SD card
            sd = MicroSDCard(spi, cs)

            # Mount filesystem
            vfs = uos.VfsFat(sd)
            uos.mount(vfs, self.data_addr)
            self.status = True
            # if self.do_file_setup:
            #     return self.packet_setup()
        except Exception as e:
            self.status = False
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > SETUP > SDCARD > {e}\n')
    def read(self):
        """
        Dummy method that does nothing, added to avoid errors in other parts of the code.

        Returns:
            None: Always returns None.
        """
        return None

def main():
    SDCard().setup()


if __name__ == '__main__':
    main()
