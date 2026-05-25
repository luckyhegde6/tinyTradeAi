import smbus
from PIL import Image, ImageDraw

class SSD1306:
    def __init__(self, bus=0, addr=0x3C):
        self.bus = smbus.SMBus(bus)
        self.addr = addr
        self.width = 128
        self.height = 64
        self._init_display()
    
    def _init_display(self):
        """Initialize SSD1306"""
        cmds = [0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12, 0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF]
        for cmd in cmds:
            self.bus.write_byte_data(self.addr, 0x00, cmd)
    
    def display_image(self, pil_image):
        """Display PIL Image on OLED (converts row-major to SSD1306 page format)"""
        if pil_image.size != (self.width, self.height):
            pil_image = pil_image.resize((self.width, self.height))
        
        pixels = pil_image.load()
        for page in range(8):
            self.bus.write_byte_data(self.addr, 0x00, (0xB0 + page))
            self.bus.write_byte_data(self.addr, 0x00, 0x00)
            self.bus.write_byte_data(self.addr, 0x00, 0x10)
            
            for col in range(self.width):
                byte = 0
                for bit in range(8):
                    if pixels[col, page * 8 + bit] > 0:
                        byte |= (1 << bit)
                self.bus.write_byte_data(self.addr, 0x40, byte)
    
    def clear(self):
        """Clear display"""
        blank = Image.new('1', (self.width, self.height), 0)
        self.display_image(blank)

    def display(self, image):
        """Luma-compatible display method - takes PIL Image and shows it"""
        self.display_image(image)

# Usage example
if __name__ == "__main__":
    device = SSD1306(bus=0, addr=0x3C)
    
    # Create test image
    img = Image.new('1', (128, 64), 0)
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "TinyTrade AI", fill=1)
    draw.text((10, 25), "Python 3.5.3", fill=1)
    
    device.display_image(img)
    print("Display OK!")