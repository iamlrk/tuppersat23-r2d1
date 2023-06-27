"""
tuppersat.gps_airborne
David Murphy (with additions by R Jeffrey)

A library to select the Dynamical Platform Models on a uBlox GPS unit.

The GPS module supports different "dynamic models" which impose various
different constraints and optimise the positioning capabilities for different
applications. In the default dynamic mode 0, the module will not give any
telemetry above 12km. You need to change the dynamic model to mode 6 -
"Airborne <1g” in order to ensure operation as high as 50km.

To use, include something like the following in your code:

>>> from machine import UART, Pin
>>> from airborne import set_airborne_mode
>>> uart = UART(0, 9600, tx_pin=Pin(4), rx_pin=Pin(5))
>>> set_airborne_mode(uart)

The message formats are described under CFG-NAV5 in "u-blox 7 Receiver
Description" (GPS.G7-SW12001-B1) pg 107

version 2023-04-12: adapted to work with Micropython & Pi Pico
- remove logging
- remove serial port

"""

import binascii
import time

AIRBORNE = 6

MODES = ['Portable', None, 'Stationary', 'Pedestrian', 'Automotive', 'Sea', 
         'Airborne < 1g', 'Airborne < 2g','Airborne < 4g']


POLLNAV = bytearray([0xB5, 0x62, 0x06, 0x24, 0x00, 0x00])
SETNAV = bytearray([0xB5, 0x62, 0x06, 0x24, 0x24, 0x00, 0x01, 0x00, 
                    0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
                    0x00, 0x00])
SAVECONF = bytearray([0xB5, 0x62, 0x06, 0x09, 0x0D, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x17])

ACKCLASS = bytearray([0x05, 0x01])


def log_info(msg):
    with open('data/logs.log', 'a') as logs:
        logs.write(f"gps_airborne.py : {msg}")

def bytes_to_hexstring(b, sep=' ', upper=True):
    _hex = binascii.hexlify(b, sep).decode('ascii')
    if upper:
        return _hex.upper()
    return _hex

# ****************************************************************************
# 
# ****************************************************************************

def lowercase_no_whitespace(s):
    """Remove all whitespace from string and make it lowercase"""
    return ''.join(s.split()).lower()

MODELS_LOOKUP = {
    lowercase_no_whitespace(model) : i
    for i, model in enumerate(MODES) if model
}

def lookup_model(model):
    """Takes model name or number and returns model number."""
    if isinstance(model, int):
        return model
    
    return MODELS_LOOKUP[lowercase_no_whitespace(model)]

def setnav(mode):
    _setnav = SETNAV[:]
    _setnav[8] = mode
    return _setnav

# ****************************************************************************
# top level interface
# ****************************************************************************

def set_dynamic_platform_model(port, model):
    """Choose dynamic platform model for UBLOX7."""
    # allow string or integer input to specify model
    mode = lookup_model(model)

    # set the dynamic platform model
    navMode = poll_gps_nav_mode(port)

    while navMode != mode:
        set_gps_nav_mode(port, mode)
        navMode = poll_gps_nav_mode(port)

    save_gps_config(port)

def set_airborne_mode(uart):
    """Set the UBLOX7 to airborne mode for operation above 12km."""
    return set_dynamic_platform_model(uart, model=AIRBORNE)
    

# ****************************************************************************
# high level UBLOX tasks
# ****************************************************************************

def set_gps_nav_mode(port, mode):
    log_info('Attempting to set GPS mode to {}...'.format(MODES[mode]))
    ackmessage(setnav(mode), port)
    log_info('{} sent.'.format(MODES[mode]))

def poll_gps_nav_mode(port):
    log_info('Polling GPS nav mode...')
    modelmessage = ackpoll(POLLNAV, port)
    navMode = modelmessage[8]
    log_info('GPS nav mode is {}.'.format(MODES[navMode]))
    return navMode

def save_gps_config(port):
    log_info('Saving GPS configuration...')
    ackmessage(SAVECONF, port)
    log_info('GPS configuration saved.')
    
# ****************************************************************************
# low level UBLOX functions
# ****************************************************************************

def calcchecksum(msg):
    chk1 = 0
    chk2 = 0
    for msgbyte in msg:
        chk1 += msgbyte
        chk2 += chk1
    chk1 %= 256
    chk2 %= 256
    return bytearray([chk1, chk2])


def checkmsg(msg):
    checkable = msg[2:-2]
    checksum = msg[-2:]
    calcedcheck = calcchecksum(checkable)
    return checksum == calcedcheck


def addcheck(msg):
    checkable = msg[2:]
    checksum = calcchecksum(checkable)
    return msg + checksum


def sendmsg(msg, port):
    _msg = bytes(msg) + b"\r\n"
    log_info(f"Sending {bytes_to_hexstring(_msg)}")
    port.write(_msg)


def readUBX(port):
    msgclass = port.read(2)
    length = port.read(2)
    lengthnum = length[0] + 256 * length[1]
    payload = port.read(lengthnum)
    checksum = port.read(2)
    fullmsg = bytearray([0xB5, 0x62]) + msgclass + length + payload + checksum
    if checkmsg(fullmsg):
        return fullmsg
    else:
        return None


def waitformsg(port, timeout = 2):
    prevByte = None
    starttime = time.time()
    while (time.time() - starttime) < timeout:
        received = port.read(1)
        if received == b'\x62' and prevByte == b'\xb5':
            return readUBX(port)
        prevByte = received

    # TODO: remove this log step?
    log_info("Waiting for message -- timeout")
    return None

def ackmessage(msg, port):
    acknowledged = False
    while not acknowledged:
        sendmsg(addcheck(msg), port)
        ackmsg = waitformsg(port)
        if ackmsg:
            msgclass = ackmsg[2:4]
            if msgclass == ACKCLASS:
                acknowledged = True	


def ackpoll(msg, port):
    pollclass = msg[2:4]
    acknowledged = False
    while not acknowledged:
        sendmsg(addcheck(msg), port)
        pollmsg = waitformsg(port)
        if pollmsg:
            recvpollclass = pollmsg[2:4]
            if recvpollclass == pollclass:
                ackmsg = waitformsg(port)
                if ackmsg:
                    msgclass = ackmsg[2:4]
                    if msgclass == ACKCLASS:
                        acknowledged = True
    return pollmsg






