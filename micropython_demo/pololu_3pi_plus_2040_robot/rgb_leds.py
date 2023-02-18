from machine import Pin, SPI
from micropython import const

class RGBLEDs():
    def __init__(self, led_count = 6):
        self.sck_pin = Pin(6)
        self.spi = SPI(id=0, baudrate=20000000, polarity=0, phase=0,
                       sck=self.sck_pin, mosi=Pin(3), miso=Pin(0))

        # fix the mode of Pin 0
        Pin(0).init(Pin.OUT, value=0)

        # initialize the data array
        self._led_count = led_count
        self.data = bytearray(
            4 +
            led_count*4 +
            (led_count + 14) // 16
            )
        self.set_brightness(31)

        self.off()

    def show(self):
        self.sck_pin.init(mode=Pin.ALT, alt=1)
        self.spi.write(self.data)
        self.sck_pin(0)
        self.sck_pin.init(mode=Pin.OUT)

    def set_brightness(self, value, led=None):
        if led != None:
            self.data[4 + led*4] = 0xe0 | (value & 0x1f)
        else:
            for l in range(self._led_count):
                self.set_brightness(value, led=l)

    def set(self, led, rgb):
        self.data[4 + led*4 + 1] = rgb[2]
        self.data[4 + led*4 + 2] = rgb[1]
        self.data[4 + led*4 + 3] = rgb[0]
    
    def set_hsv(self, led, hsv, h_scale = 360):
        self.set(self, led, self.hsv2rgb(led, hsv[0], hsv[1], hsv[2], h_scale))

    def hsv2rgb(self, h, s, v, h_scale = 360):
        # adapted from https://stackoverflow.com/a/14733008
        # but with variable hue scale
        sixth = (h_scale + 3) // 6
        if s == 0:
            return [v, v, v]

        h = h % h_scale
        region = h // sixth
        remainder = (h - (region * sixth)) * 6
        p = (v * (255 - s)) // 256
        q = (v * (255 - ((s * remainder) // h_scale))) // 256
        t = (v * (255 - ((s * (h_scale - remainder)) // h_scale))) // 256

        if region == 0:
            return [v, t, p]
        elif region == 1:
            return [q, v, p]
        elif region == 2:
            return [p, v, t]
        elif region == 3:
            return [p, q, v]
        elif region == 4:
            return [t, p, v]
        else:
            return [v, p, q]
        
    def off(self):
        for led in range(self._led_count):
            self.set(led, [0, 0, 0])
        self.show()
