# Rule: I2C Hardware Safety

## Bus Access
- Always wrap I2C bus operations in try/except. A missing device must never crash the app.
- Use `i2cdetect -y -r 0` (read-mode) for scanning. Never use `-q` (quick-write) on PCF8574 — it sends random data to the LCD.
- Close bus handles with `try/finally` to avoid leaking file descriptors.

## Address Conflicts
The kernel `rda-sensor` driver claims I2C address 0x3C at boot. If the OLED is not detected:
1. Unbind: `echo 0-003c > /sys/bus/i2c/drivers/rda-sensor/unbind`
2. Blacklist: add `blacklist rda-sensor` to `/etc/modprobe.d/`
3. Verify with `i2cdetect -y -r 0`

## Power
- LCD VCC → Orange Pi Pin 2 or 4 (5V), NOT Pin 1 (2.8V)
- Use a dedicated 5V/2A wall charger. Laptop USB ports cause brownouts.
- Common GND between all devices.

## Pin Mapping (I2C Bus 0)
- Pin 3: SDA (I2C Data)
- Pin 5: SCL (I2C Clock)
- Pull-up resistors: 4.7kΩ on SDA/SCL (built-in on Orange Pi 2G-IOT)
