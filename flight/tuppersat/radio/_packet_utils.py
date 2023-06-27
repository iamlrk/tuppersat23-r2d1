"""tuppersat.radio._packet_utils.py

Simplified functions to format packets as bytes objects.

"""

def format(value, fmtspec):
    _s = '{:'+fmtspec+'}'
    return _s.format(value)

def format_fixed_width(value, width, fmt_spec):
    """Returns fixed width string with format(value, fmt_spec)."""
    try:
        _value = (format(value, fmt_spec) if value is not None else '')
    except ValueError as e:
        _rfmt_spec, _rvalue = repr(fmt_spec), repr(value) 
        msg = f"Invalid format specifier {_rfmt_spec} for value {_rvalue}"
        raise ValueError(msg) from e

    return '{val:<{w}}'.format(val=_value, w=width)

# ****************************************************************************
# Telemetry Packets

def strftime(time):
    hh, mm, ss = time.hour, time.minute, time.second
    return f"{hh:0>2}{mm:0>2}{ss:0>2}"

def format_fixed_width_time(time, width=6):
    return (' '*width if time is None else strftime(time))

def TelemetryPacket(callsign, index, hhmmss=None,
                    latitude=None, longitude=None, hdop=None, altitude=None,
                    t_internal=None, t_external=None, pressure=None):
    """Assemble TelemetryPacket as formatted bytes object."""


    _fields = [
        format_fixed_width(callsign  ,  8, '<8'      ),
        format_fixed_width(index     ,  5, '>05'     ),
        format_fixed_width_time(hhmmss,  6),
        format_fixed_width(latitude  ,  9, '+09.05f' ),
        format_fixed_width(longitude , 10, '+010.05f'),
        format_fixed_width(hdop      ,  5, '05.02f'  ), 
        format_fixed_width(altitude  ,  8, '08.02f'  ), 
        format_fixed_width(t_internal,  8, '+08.03f' ), 
        format_fixed_width(t_external,  8, '+08.03f' ), 
        format_fixed_width(pressure  ,  9, '09.04f'  ),
    ]

    _parts = '|'.join(_fields)
    pkt_string = f'T|{_parts}'
    return pkt_string.encode('ascii')


# ****************************************************************************
# Data Packets

def DataPacket(callsign, data):
    """Assemble DataPacket as formatted bytes object."""

    # format and encode callsign
    _callsign_string = format_fixed_width(callsign, 8, '<8')
    _callsign_bytes = _callsign_string.encode('ascii')

    # assemble and return
    pkt_bytes = b'D|' + _callsign_bytes + b'|' + bytes(data)
    return pkt_bytes
