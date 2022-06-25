import machine
import gc
from drivers.ssd1351.ssd1351 import SSD1351 as SSD

height = 128  # height = 128 # 1.5 inch 128*128 display

pdc = machine.Pin(20, machine.Pin.OUT, value=0)
pcs = machine.Pin(17, machine.Pin.OUT, value=1)
prst = machine.Pin(21, machine.Pin.OUT, value=1)
spi = machine.SPI(0,
                  baudrate=10000000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, height)  # Create a display instance
