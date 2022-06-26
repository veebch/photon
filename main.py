# main.py - a script for making a tlight meter, running using a Raspberry Pi Pico
# First prototype is using an OLED, rotary encoder and a photodiode
# The display uses drivers made by Peter Hinch [link](https://github.com/peterhinch/micropython-nano-gui)

# Released under the GPL 3.0

# Fonts for Writer (generated using https://github.com/peterhinch/micropython-font-to-py)
import gui.fonts.freesans20 as freesans20
import gui.fonts.quantico40 as quantico40
from gui.core.writer import CWriter
from gui.core.nanogui import refresh
import utime
from machine import Pin,I2C, SPI,ADC
from rp2 import PIO, StateMachine, asm_pio
import sys
import math
import gc
# Display setup
from drivers.ssd1351.ssd1351_16bit import SSD1351 as SSD
# Look for thermometer (add OLED complaint if one can't be seen)

height = 128
photoPIN = 26  
pdc = Pin(20, Pin.OUT, value=0)
pcs = Pin(17, Pin.OUT, value=1)
prst = Pin(21, Pin.OUT, value=1)
spi = SPI(0,
                  baudrate=10000000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=SPI.MSB,
                  sck=Pin(18),
                  mosi=Pin(19),
                  miso=Pin(16))
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, height)  # Create a display instance
ssd.fill(0)

wri = CWriter(ssd,freesans20, fgcolor=SSD.rgb(255,255,255),bgcolor=0)
CWriter.set_textpos(ssd, 45,51)
wri.printstring('Light')
CWriter.set_textpos(ssd, 90,25)
wri.printstring('veeb.ch/')

ssd.show()
utime.sleep(4)

# define encoder pins 

switch = Pin(4, mode=Pin.IN, pull = Pin.PULL_UP) # inbuilt switch on the rotary encoder, ACTIVE LOW
outA = Pin(2, mode=Pin.IN) # Pin CLK of encoder
outB = Pin(3, mode=Pin.IN) # Pin DT of encoder

# Define relay and LED pins

ledPin = Pin(25, mode = Pin.OUT, value = 0) # Onboard led on GPIO 25


# define global variables
counter = 0   # counter updates when encoder rotates
direction = "" # empty string for registering direction change
outA_last = 0 # registers the last state of outA pin / CLK pin
outA_current = 0 # registers the current state of outA pin / CLK pin

button_last_state = False # initial state of encoder's button 
button_current_state = "" # empty string ---> current state of button

# Read the last state of CLK pin in the initialisaton phase of the program 
outA_last = outA.value() # lastStateCLK

# interrupt handler function (IRQ) for CLK and DT pins
def encoder(pin):
    # get global variables
    global counter
    global direction
    global outA_last
    global outA_current
    global outA
    
    # read the value of current state of outA pin / CLK pin
    try:
        outA_current = outA.value()
    except:
        print('outA not defined')
        outA_current = 0
        outA_last = 0
    # if current state is not same as the last stare , encoder has rotated
    if outA_current != outA_last:
        # read outB pin/ DT pin
        # if DT value is not equal to CLK value
        # rotation is clockwise [or Counterclockwise ---> sensor dependent]
        if outB.value() != outA_current:
            counter -= .05
        else:
            counter += .05
        
    # update the last state of outA pin / CLK pin with the current state
    outA_last = outA_current
    counter=min(90,counter)
    counter=max(45,counter)
    return(counter)
    

# interrupt handler function (IRQ) for SW (switch) pin
def button(pin):
    # get global variable
    global button_last_state
    global button_current_state
    if button_current_state != button_last_state:
        utime.sleep(.2)       
        button_last_state = button_current_state
    return

# Screen to display on OLED during heating
def displaynum(num,temperature):
    #This needs to be fast for nice responsive increments
    #100 increments?
    delta=num-temperature
    text=SSD.rgb(0,255,0)
    wri = CWriter(ssd,quantico40, fgcolor=text,bgcolor=0)
    CWriter.set_textpos(ssd, 35,0)  # verbose = False to suppress console output
    wri.printstring(str("{:.1f}".format(num))+" ")
    wrimem = CWriter(ssd,freesans20, fgcolor=SSD.rgb(255,255,255),bgcolor=0)
    CWriter.set_textpos(ssd, 105,0)  
    wrimem.printstring(str("{:.1f}".format(temperature)))
    CWriter.set_textpos(ssd,105,90)  
    wrimem.printstring("64")
    wrimem = CWriter(ssd,freesans20, fgcolor=0,bgcolor=SSD.rgb(100,100,40))
    CWriter.set_textpos(ssd,82,90)
    wrimem.printstring(" iso ")
    ssd.show()
    return

def readLight(photoGP):
    photoRes = ADC(Pin(photoGP))
    light = photoRes.read_u16() # with no transform to brightness
    return light

def beanaproblem(string):
    refresh(ssd, True)  # Clear any prior image
    relaypin = Pin(15, mode = Pin.OUT, value =0 )
    utime.sleep(2)
    
# Attach interrupt to Pins

# attach interrupt to the outA pin ( CLK pin of encoder module )
outA.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
              handler = encoder)

# attach interrupt to the outB pin ( DT pin of encoder module )
outB.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING ,
              handler = encoder)

# attach interrupt to the switch pin ( SW pin of encoder module )
switch.irq(trigger = Pin.IRQ_FALLING ,
           handler = button)


# Main Logic
pin=0
counter= 44
lastupdate = utime.time()  
refresh(ssd, True)  # Initialise and clear display.

lasterror = 0
# The Tweakable values that will help tune for our use case. TODO: Make accessible via menu on OLED
output=0
while True:
    counter=encoder(pin)
    temp = readLight(photoPIN)
    displaynum(counter,float(temp))
    button_last_state = False # reset button last state to false again ,
                              # totally optional and application dependent,
                              # can also be done from other subroutines
                              # or from the main loop
    #utime.sleep(1)
    now = utime.time()
