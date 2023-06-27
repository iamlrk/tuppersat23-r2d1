"""tuppersat.radio._rhserial_radio.py

Interface to the rhserial library using UART compatible with the Raspberry Pi
Pico. 

"""

# tuppersat imports
import tuppersat.rhserial as rhserial

# local imports
from ._utils import Counter


BROADCAST = 0xFF

class RHSerialRadio:
    """Transmit-only interface to RHSerial via UART."""
    def __init__(self, uart, address=0xFF):
        """Initialiser."""
        # UART stream interface
        self.uart = uart

        # address (used for msgfrom)
        self.address = address

        # counter object to track frames (used for msgid)
        self.frame_count = Counter(modulo=0x100)
        
    # user interface to send messages

    def send_bytes(self, msgbytes, to=BROADCAST, flag=0x00):
        """Pack and transmit encoded bytes message."""
        _msg = rhserial.pack_message(
            msgbytes = msgbytes          ,
            msgto    = to                ,
            msgfrom  = self.address      ,
            msgid    = self.frame_count(),
            msgflag  = flag
        )
        return self.uart.write(_msg)
    
    def send_text(self, msg, to=BROADCAST, flag=0x00, encoding='utf-8'):
        """Encode, pack and transmit a text string."""
        _msgbytes = msg.encode(encoding)
        return self.send_bytes(msgbytes, to, flag)


    
