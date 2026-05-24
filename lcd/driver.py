import time
from utils.helpers import setup_logger

logger = setup_logger("LCD_Driver", log_to_file=True)

# PCF8574 range: 0x20-0x27, PCF8574A range: 0x38-0x3F
I2C_LCD_KNOWN_ADDRESSES = [0x27, 0x3F, 0x38, 0x39, 0x3E]


class PCF8574LCD:
    BACKLIGHT_ON = 0x08
    BACKLIGHT_OFF = 0x00

    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x8DOTS = 0x00

    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    LCD_RS = 0x01
    LCD_RW = 0x02
    LCD_E = 0x04
    LCD_D4 = 0x10
    LCD_D5 = 0x20
    LCD_D6 = 0x40
    LCD_D7 = 0x80

    def __init__(self, i2c_bus, i2c_address=0x27, columns=16, rows=2):
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.columns = columns
        self.rows = rows
        self.backlight = self.BACKLIGHT_ON
        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self._write_byte(0x00)
        time.sleep(0.05)
        self._init_lcd()

    def _write_byte(self, byte):
        self.i2c_bus.write_byte(self.i2c_address, byte)

    def _strobe(self, data):
        combined = data | self.LCD_E | self.backlight
        self._write_byte(combined)
        time.sleep(0.0005)
        self._write_byte(combined & ~self.LCD_E)
        time.sleep(0.0001)

    def _send_nibble(self, nibble, rs_mode):
        self._strobe(((nibble << 4) & 0xF0) | rs_mode)

    def _send_byte(self, byte, rs_mode):
        self._strobe((byte & 0xF0) | rs_mode)
        self._strobe(((byte << 4) & 0xF0) | rs_mode)

    def _write_cmd(self, cmd):
        self._send_byte(cmd, 0x00)

    def _write_data(self, data):
        self._send_byte(data, self.LCD_RS)

    def _init_lcd(self):
        self._send_nibble(0x03, 0x00)
        time.sleep(0.005)
        self._send_nibble(0x03, 0x00)
        time.sleep(0.0001)
        self._send_nibble(0x03, 0x00)
        time.sleep(0.0001)
        self._send_nibble(0x02, 0x00)
        time.sleep(0.0001)
        self._write_cmd(self.LCD_FUNCTIONSET | self.LCD_2LINE | self.LCD_5x8DOTS)
        self._write_cmd(self.LCD_DISPLAYCONTROL | self.displaycontrol)
        self.clear()
        self._write_cmd(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT)
        self.display(True)

    def clear(self):
        self._write_cmd(self.LCD_CLEARDISPLAY)
        time.sleep(0.002)

    def home(self):
        self._write_cmd(self.LCD_RETURNHOME)
        time.sleep(0.002)

    def display(self, on=True):
        ctrl = self.LCD_DISPLAYON if on else self.LCD_DISPLAYOFF
        ctrl |= self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.displaycontrol = ctrl
        self._write_cmd(self.LCD_DISPLAYCONTROL | ctrl)

    def set_cursor(self, col, row):
        offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self.rows:
            row = self.rows - 1
        self._write_cmd(self.LCD_SETDDRAMADDR | (col + offsets[row]))

    def write_text(self, text, col=0, row=0):
        self.set_cursor(col, row)
        for ch in str(text)[:self.columns]:
            self._write_data(ord(ch))

    def write_line(self, text, row=0):
        padded = str(text).ljust(self.columns)[:self.columns]
        self.write_text(padded, 0, row)

    def set_backlight(self, on=True):
        self.backlight = self.BACKLIGHT_ON if on else self.BACKLIGHT_OFF
        self._write_byte(self.backlight)

    def close(self):
        self.clear()
        self.set_backlight(False)
        self._write_byte(0x00)
