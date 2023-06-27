"""tuppersat.radio._tuppersat_radio.py
University College, Dublin

Provides class TupperSatRadio to handle transmitting TDRSS formatted data and
telemetry packets.

"""

# tuppersat imports
#from tuppersat.packets import TelemetryPacket, DataPacket
#from tuppersat.toolkit.misc import Counter

# local imports
from ._utils import Counter
from ._rhserial_radio import RHSerialRadio
from ._packet_utils import TelemetryPacket, DataPacket

def format_callsign(callsign):
    #TODO: validate ascii characters?
    #TODO: validate length limit?
#    return callsign.ljust(8)[:8]
    callsign = callsign[:8]
    return f"{callsign:<8}"


class TupperSatRadio(RHSerialRadio):
    """API to send TDRSS telemetry & data messages with the T3."""
    
    def __init__(self, uart, address, callsign, user_callback=None):
        """Initialiser."""
        self.callsign = format_callsign(callsign)
        self.telemetry_count = Counter()
        
#        super().__init__(uart, address, user_callback)
        super().__init__(uart, address)

    def send_packet(self, packet):
        """Convert pkt to bytes and transmit."""
        #TODO: check pkt is a valid packet type?
        #TODO: catch exceptions when converting to bytes?
        # convert to bytes
        _pkt_bytes = bytes(packet)

        # transmit
        return self.send_bytes(_pkt_bytes)
        
    def send_telemetry(self, hhmmss, latitude, longitude, hdop, altitude,
                       t_internal, t_external, pressure):
        """Assemble and transmit a TupperSat telemetry packet."""
        # assemble
        _packet = TelemetryPacket(
            callsign   = self.callsign         , 
            index      = self.telemetry_count(), 
            hhmmss     = hhmmss                , 
            latitude   = latitude              ,
            longitude  = longitude             ,
            hdop       = hdop                  ,
            altitude   = altitude              ,
            t_internal = t_internal            ,
            t_external = t_external            ,
            pressure   = pressure              ,
        )

        # transmit
        return self.send_packet(_packet)

    def send_data(self, data):
        """Assemble and transmit data in a TupperSat data packet."""
        # assemble
        _packet = DataPacket(
            callsign = self.callsign,
            data     = bytes(data)  ,
        )

        # transmit
        return self.send_packet(_packet)
