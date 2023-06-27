"""
_rhserial.py

A Python implementation of the RadioHead LoRa API.

The message packet format is that defined by the RadioHead RH_Serial
class, with start byte, a 4 byte header, the message, an end byte, and a
checksum. There is a minor modification to replace the message flag byte
with an RSSI indication byte. 

For further details of the format, see
www.airspayce.com/mikem/arduino/RadioHead/classRH__Serial.html

"""

# standard library imports
import struct

# third party imports
#import crcmod.predefined

# local imports
from . import DLE, STX, ETX
from ._crc_16_mcrf4xx import crc_16_mcrf4xx as crc16

# ****************************************************************************
# checksum functions
# ****************************************************************************

# checksum object
#crc16 = crcmod.predefined.mkCrcFun('crc-16-mcrf4xx')

def calculate_checksum(message):
    return bytearray(struct.pack(">H", crc16(message)))

def passes_checksum(message, checksum):
    return checksum == calculate_checksum(message)


# ****************************************************************************
# packet handling
# ****************************************************************************

def unpack_message(msg):
    """Extract message header and body from msg bytearray.

    NB, the input msg bytearray, should contain only the 4 header bytes and the
    message payload. The initial DLE+STX and the final DLE+ETX+CHECKSUM bytes
    should be removed before passing to this function.
    """
    # extract header information as integers
    msgto, msgfrom, msgid, rawrssi = msg[:4]

    # normalise the signal strength indicator to range [-128, 127]
    msgrssi = (rawrssi - 256 if rawrssi > 127 else rawrssi)

    # extract message payload as a bytes object
    payload = bytes(msg[4:])

    # return dictionary with header fields and message payload
    msgdict = {
        'to'     : msgto  ,
        'from'   : msgfrom,
        'id'     : msgid  ,
        'rssi'   : msgrssi,
        'message': payload,
    }

    return msgdict

def pack_message(msgbytes, msgto, msgfrom, msgid, msgflag=0x00):
    """Assemble message packet, including DLE stuffing."""
    # TODO: should include check that all values are in right range (or
    # catch ValueError and return a useful error message???)

    # TODO: we adapt the onboard firmware to replace the msgflag with an
    # RSSI byte. Should we therefore hide the msgflag in this API, or
    # maybe hardcode it to 0x00?

    # message header
    msghead = DLE+STX
    # message tail
    msgtail = DLE+ETX
    # message body
    msginfo = bytearray([msgto, msgfrom, msgid, msgflag])
    msgbody = bytes(msginfo) + bytes(msgbytes)
    # calculate checksum
    checkable = msgbody + msgtail
    checksum  = calculate_checksum(checkable)

    # perform DLE stuffing, replacing the escape byte \x10 with \x10\x10
    # for any occurances in the message itself, or in the (to, from, id,
    # flag) header information.
    msgbody = msgbody.replace(DLE, DLE+DLE)

    # finally, assemble and return full message
    full_msg = msghead + msgbody + msgtail + bytes(checksum)
    return full_msg
