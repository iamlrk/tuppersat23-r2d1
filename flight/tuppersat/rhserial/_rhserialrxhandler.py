"""_rhserialrxhandler.py

Provides class implementing Airspayce Radiohead RX state machine.

For further details of the format, see
www.airspayce.com/mikem/arduino/RadioHead/classRH__Serial.html

"""
# local imports
from . import DLE, STX, ETX
from . import passes_checksum

class RXHandler:
    """State machine to handle RHSerial messages.

    For further details of the format, see
    www.airspayce.com/mikem/arduino/RadioHead/classRH__Serial.html

    """
    def __init__(self, on_received):
        """Initialiser.

        Parameters
        ----------
        on_received : callable
            callback function which takes completed message as its sole 
             argument.
        """
        self._on_received = on_received
        self.reset()

    def __call__(self, byte):
        return self.update(byte)

    @property
    def state(self):
        return self._state

    def reset(self):
        """Reset the RXHandler state."""
        self._state = 'IDLE'
        self._message = bytearray()
        self._checksum = bytearray()

    def update(self, byte):
        """Handle a new byte and update state machine."""
        # cache the starting state for later logging
        _old_state = self.state

        # TODO: reset state machine if bad byte passed?
        # TODO: handle integer byte values?
        if byte:
            if _old_state == 'IDLE':
                # looking for a DLE to start
                if byte == DLE:
                    # Got a DLE, enter STX state
                    self._state = 'STX'
                # ignore anything else
                else:
                    pass
            elif _old_state == 'STX':
                # looking for a STX to begin reading message
                if byte == STX:
                    # got a STX, enter MESSAGE state and clear out message
                    self._state = 'MESSAGE'
                    self._message = bytearray()
                else:
                    # didn't get STX, go back to IDLE
                    self._state = 'IDLE'
            elif _old_state == 'MESSAGE':
                # looking for DLEs to either escape a DLE or end the message
                if byte == DLE:
                    # got a DLE, enter MSGDLE state.
                    self._state = 'MSGDLE'
                else:
                    # it's part of the message, add it to the message.
                    self._message += byte
                    #TODO: check message length???
            elif _old_state == 'MSGDLE':
                # looking for a DLE or a ETX.
                if byte == DLE:
                    # it's a DLE that's part of the message.
                    self._message += byte
                    state = 'MESSAGE'
                elif byte == ETX:
                    # it's an ETX, we're done with the message, move on to the
                    # checksum.
                    self._state = 'CHECKSUM1'
                    self._checksum = bytearray()
                else:
                    # this shouldn't have happened. Let's abort and go back to
                    # the IDLE state
                    self._state = 'IDLE'
            elif _old_state == 'CHECKSUM1':
                self._checksum += byte
                self._state = 'CHECKSUM2'
            elif _old_state == 'CHECKSUM2':
                self._checksum += byte
                # all done, let's check the sum and process the message
                if passes_checksum(self._message+DLE+ETX, self._checksum):
                    # Process message.
                    self._on_received(self._message)
                # either we processed the message or it didn't pass the
                # checksum, either way let's start over
                self._state = 'IDLE'

        # return the new state, just in case someone wants to use it later
        return self._state

