import time
import machine
from ustruct import unpack

_VEML6075_ADDR = const(0x10)

_REG_CONF = const(0x00)
_REG_UVA = const(0x07)
_REG_DARK = const(0x08)  # check is true?
_REG_UVB = const(0x09)
_REG_UVCOMP1 = const(0x0A)
_REG_UVCOMP2 = const(0x0B)
_REV_ID = const(0x0C)

# Valid constants for UV Integration Time
_VEML6075_UV_IT = {50: 0x00, 100: 0x01, 200: 0x02, 400: 0x03, 800: 0x04}


class UV:
    def __init__(self,
                 bus=0,
                 sda=0,
                 scl=1,
                 freq=400000,
                 integration_time=50,
                 high_dynamic=True,
                 uva_a_coef=2.22,
                 uva_b_coef=1.33,
                 uvb_c_coef=2.95,
                 uvb_d_coef=1.74,
                 uva_response=0.001461,
                 uvb_response=0.002591) -> None:
        self.uvb = None
        self.uva = None
        self.i2c = None
        self.bus = bus
        self.sda = sda
        self.scl = scl
        self.freq = freq
        self._addr = _VEML6075_ADDR
        self._a = uva_a_coef
        self._b = uva_b_coef
        self._c = uvb_c_coef
        self._d = uvb_d_coef
        self._uvaresp = uva_response
        self._uvbresp = uvb_response
        self._uvacalc = self._uvbcalc = None
        self.high_dynamic = high_dynamic
        self.integration_time_s = integration_time

    def setup(self):
        try:
            self.i2c = machine.I2C(self.bus, sda=machine.Pin(self.sda), scl=machine.Pin(self.scl), freq=self.freq)
            veml_id = self._read_register(_REV_ID)
            if veml_id != 0x26:
                raise RuntimeError("Incorrect VEML6075 ID 0x%02X" % veml_id)
            # shut down
            self._write_register(_REG_CONF, 0x01)
            # Set integration time
            self.integration_time = self.integration_time_s
            # enable
            conf = self._read_register(_REG_CONF)
            if self.high_dynamic:
                conf |= 0x08
            conf &= ~0x01  # Power on
            self._write_register(_REG_CONF, conf)
            if self.i2c == 'None':
                print('hello')
                # TODO: write default conditions
                sensor_status = 'broky'
        except:
            return 'brokey'
    def get_raw_data(self):
        """Perform a full reading and calculation of all UV calibrated values"""
        time.sleep(0.1)
        temp_uva = self._read_register(_REG_UVA)
        temp_uvb = self._read_register(_REG_UVB)
        # dark = self._read_register(_REG_DARK)
        uvcomp1 = self._read_register(_REG_UVCOMP1)
        uvcomp2 = self._read_register(_REG_UVCOMP2)
        # Equation 1 & 2 in App note, without 'golden sample' calibration
        self.uva = temp_uva - (self._a * uvcomp1) - (self._b * uvcomp2)
        self.uvb = temp_uvb - (self._c * uvcomp1) - (self._d * uvcomp2)
        return {'uva': self.uva, 'uvb': self.uvb}

    def read(self):
        try:
            return self.get_raw_data()
        except Exception as e:
            with open('data/logs.log', 'a') as logs:
                logs.write(f'ERROR > UV > {e}\n')
            return {'uva': 101, 'uvb': 101}

    @property
    def integration_time(self):
        """The amount of time the VEML is sampling data for, in millis.
        Valid times are 50, 100, 200, 400 or 800ms"""
        key = (self._read_register(_REG_CONF) >> 4) & 0x7
        for k, val in enumerate(_VEML6075_UV_IT):
            if key == k:
                return val
            raise RuntimeError("Invalid integration time")

    @integration_time.setter
    def integration_time(self, val):
        if not val in _VEML6075_UV_IT.keys():
            raise RuntimeError("Invalid integration time")
        conf = self._read_register(_REG_CONF)
        conf &= ~ 0b01110000  # mask off bits 4:6
        conf |= _VEML6075_UV_IT[val] << 4
        self._write_register(_REG_CONF, conf)

    def _read_register(self, register):
        """Read a 16-bit value from the `register` location"""
        result = unpack('BB', self.i2c.readfrom_mem(self._addr, register, 2))
        return (result[1] << 8) | result[0]

    def _write_register(self, register, value):
        """Write a 16-bit value to the `register` location"""
        self.i2c.writeto_mem(self._addr, register, bytes([value, value >> 8]))


def main():
    uv = UV()
    uv.setup()
    while True:
        uva = uv.read()
        print(uva)
        # print(f'UVa = {uva}\nUVb = {uva}')
        print('-' * len(str(uva)) * 5)
        time.sleep(2)


if __name__ == '__main__':
    main()

