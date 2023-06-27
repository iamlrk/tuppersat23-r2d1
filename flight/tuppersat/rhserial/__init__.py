"""tuppersat.rhserial
University College Dublin

A Python implementation of the RadioHead LoRa API.

The message packet format is that defined by the RadioHead RH_Serial class,
with start byte, a 4 byte header, the message, an end byte, and a
checksum. There is a minor modification to replace the message flag byte with
an RSSI indication byte.

For further details of the format, see
www.airspayce.com/mikem/arduino/RadioHead/classRH__Serial.html

------------
API Overview
------------

The core API consists of functions `pack_message` and `unpack_message`, which
handle packet and header formatting. Note that they aren't quite symmetric, in
particular around handling DLE-escape sequences and the message head and
tail. The RXHandler class contains a state machine that will process receiving
a message one byte at a time.

"""

# byte codes for DLE, STX, ETX.
DLE = b'\x10' # Data Link Escape
STX = b'\x02' # Start of Text
ETX = b'\x03' # End of Text


from ._rhserial import pack_message, unpack_message
from ._rhserial import calculate_checksum, passes_checksum
from ._rhserialrxhandler import RXHandler
#from ._rhserialradio import RHSerialRadio
