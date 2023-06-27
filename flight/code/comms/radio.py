# standard library imports
from time import sleep

# uPython imports
from machine import UART, Pin

# tuppersat imports
from tuppersat.radio import TupperSatRadio


class Radio:

    def __init__(self, uart_id=1, tx_pin=4, rx_pin=5, t3_baudrate=38400, add=0x15, call='R2D1'):
        """
        Initializes a new Radio object.

        Args:
            uart_id (int): The UART id number. Default is 1.
            tx_pin (int): The pin number for the transmitter. Default is 4.
            rx_pin (int): The pin number for the receiver. Default is 5.
            t3_baudrate (int): The baudrate for the radio. Default is 38400.
            add (int): The radio address. Default is 0x15.
            call (str): The radio call sign. Default is 'R2D1'.
        """
        self.radio = None
        self.uart_id = uart_id
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.t3_baudrate = t3_baudrate
        self.add = add
        self.call = call

    def setup(self):
        """
        Initializes the Radio object and returns it.

        Returns:
            TupperSatRadio: The Radio object.
        
        Raises:
            TODO: Define the exception that may be raised if initialization fails.
        """
        try:
            uart = UART(self.uart_id, baudrate=self.t3_baudrate, tx=Pin(self.tx_pin), rx=Pin(self.rx_pin))
            self.radio = TupperSatRadio(uart, self.add, self.call)
            return self.radio
        except:
            print('radio fail') #TODO write an proper exception
            
    
    def transmit(self, time, group, packet, logger, packet_count, packet_rate):
        """
        Transmit a packet via the radio.

        Args:
        - time (float): A float representing the current time.
        - group (str): A string indicating the type of packet to transmit ('telemetry' or 'data').
        - packet (dict or str): A dictionary or string containing the packet to be transmitted. If `group` is 'telemetry', it must be a dictionary. If `group` is 'data', it must be a string.
        - radio (Radio): An object representing the radio used for transmission.
        - logger (Callable): A function that logs the transmission details.
        - packet_count (int): An integer representing the total number of packets transmitted.
        - packet_rate (float): A float representing the packet transmission rate.

        Returns:
        - None: The function does not return anything, but instead sends the packet via the radio and logs the transmission details using the provided logger function.

        Raises:
        - No explicit exceptions are raised, but if `group` is neither 'telemetry' nor 'data', the function logs an error message using the provided logger function.

        Example:
        >>> transmit(12.021, 'telemetry', packet, radio, print, 1, 0.5)
        12.021 > TRANSMIT > TELEMETRY > Packet Count - 1 > Packet Rate - 0.5

        >>> packet = 'Hello, world!'
        >>> transmit(22.121, 'data', packet, radio, print, 2, 0.5)
        22.121 > TRANSMIT > DATA      > Packet Count - 2 > Packet Rate - 0.5

        >>> transmit(12.021, 'invalid_group', packet, radio, print, 1, 0.5)
        wut? - Hello, world! - invalid_group
        """

        if group == 'telemetry':
            print(packet)
            self.radio.send_telemetry(**packet)
        elif group == 'data':
            self.radio.send_data(bytearray(packet.encode('ascii')))
        else:
            logger(f'wut? - {packet} - {group}')
        logger(f'{time:9} > TRANSMIT > {group.upper():9} > Packet Count - {packet_count} > Packet Rate - {packet_rate}\n')


    def loop(self, time, group, packet, logger, packet_count, packet_rate):
        """
        Sends a data or telemetry packet using the Radio object.

        Args:
            dic (dict): A dictionary representing the data or telemetry packet to be sent.
            send_DorT (str): A string indicating whether the packet is data ('data') or telemetry ('telemetry').
            pause (int): The number of seconds to pause after sending the packet. Default is 1.
        """
        if group == 'telemetry':
            print(packet)
            self.radio.send_telemetry(**packet)
        elif group == 'data':
            self.radio.send_data(bytearray(packet.encode('ascii')))
        else:
            logger(f'wut? - {packet} - {group}')
        logger(f'{time:9} > TRANSMIT > {group.upper():9} > Packet Count - {packet_count} > Packet Rate - {packet_rate}\n')


def main():
    # main loop
    pass
    # while True:
    #     loop(radio)


if __name__ == "__main__":
    main()

