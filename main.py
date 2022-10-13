# main.py - a script for making a light meter, running using a Raspberry Pi Pico
# Assumes a linear respose in brightness, calibrates from two values in a text file
# First prototype is using an OLED, rotary encoder and a pimoroni light sensor, if a strobe mode is added. This may need to change.
# The display uses drivers made by Peter Hinch [link](https://github.com/peterhinch/micropython-nano-gui)
# Tested on pico running Pimoroni uf2 pimoroni-pico-v1.19.0-micropython.uf2
  
# Released under the GPL 3.0

# Fonts for Writer (generated using https://github.com/peterhinch/micropython-font-to-py)
import gui.fonts.freesans20 as freesans20
import gui.fonts.quantico40 as quantico40
from gui.core.writer import CWriter
from gui.core.nanogui import refresh
from drivers.ssd1351.ssd1351_16bit import SSD1351 as SSD
from machine import Pin,I2C, SPI,ADC
import pimoroni_i2c
import breakout_bh1745
import utime
import sys
import math
import gc

def splash(string):
    wri = CWriter(ssd,freesans20, fgcolor=SSD.rgb(55,55,55),bgcolor=0, verbose=False)
    CWriter.set_textpos(ssd, 0,0)
    wri.printstring('{:.0f}%'.format(percentage))
    wri = CWriter(ssd,freesans20, fgcolor=SSD.rgb(50,50,0),bgcolor=0, verbose=False )
    CWriter.set_textpos(ssd, 90,25)
    wri.printstring('veeb.ch/')
    ssd.show()
    utime.sleep(.3)
    for x in range(11):
        wri = CWriter(ssd,freesans20, fgcolor=SSD.rgb(55-x,55-x,55-x),bgcolor=0, verbose=False)
        CWriter.set_textpos(ssd, 0,0)
        wri.printstring('{:.0f}%'.format(percentage))
        wri = CWriter(ssd,freesans20, fgcolor=SSD.rgb(25*x,25*x,25*x),bgcolor=0, verbose=False)
        CWriter.set_textpos(ssd, 55,25)
        wri.printstring(string)
        wri = CWriter(ssd,freesans20, fgcolor=SSD.rgb(50-x,50-x,0),bgcolor=0, verbose=False )
        CWriter.set_textpos(ssd, 90,25)
        wri.printstring('veeb.ch/')
        ssd.show()
    utime.sleep(.5)
    return

# interrupt handler function (IRQ) for CLK and DT pins
def encoder(pin):
    global outA_last
    global outA_current
    global counter
    # read the value of current state of outA pin / CLK pin
    try:
        outA_current = outA.value()
    except:
        print('outA not defined')
        outA_current = 0
        outA_last = 0
    # if current state is not same as the last stare , encoder has rotated
    if outA_current != outA_last:
        # read outB pin
        if outB.value() != outA_current:
            counter = -1
        else:
            counter = 1
    # update the last state of outA pin / CLK pin with the current state
    outA_last = outA_current
    return 
    
# interrupt handler function (IRQ) for measure button
def button(pin):
    global button_last_state
    global button_current_state
    global lastmeasure
    global red, green, blue
    if button_current_state != button_last_state:
        utime.sleep(.2)
        print("Measure")
        red,green, blue,lastmeasure=sensorread()
        button_last_state = button_current_state
        print(lastmeasure)
        with open('lastisoindex.txt', "w") as f:
            f.write(str(isoindex))
        f.close()
    return

# interrupt handler function (IRQ) for SW (switch) pin
def modebutton(pin):
    global modebutton_last_state
    global modebutton_current_state
    global mode
    global modes
    if modebutton_current_state != modebutton_last_state:
        utime.sleep(.2)
        print("Toggle Mode")
        index = modes.index(mode)
        index = (index + 1) % len(modes)
        mode = modes[index]
        print(mode)
        modebutton_last_state = modebutton_current_state
    return

# interrupt handler function (IRQ) for iso switch
def isobutton(pin):
    global isobutton_last_state
    global isobutton_current_state
    global isoadjust
    if isobutton_current_state != isobutton_last_state:
        utime.sleep(.2)
        isoadjust = not isoadjust
        isobutton_last_state = isobutton_current_state
    return

# read the value from the light sensor
def sensorread():
    rgbc_raw = bh1745.rgbc_raw()
    rgb_clamped = bh1745.rgbc_clamped()
    brightness=rgbc_raw[3]
    print("Clamped: {}, {}, {}, {}".format(*rgb_clamped))
    print("Bright="+str(brightness))
    try:
        EV = math.log2(brightness/2.5)+evcorrection
    except:
        EV = -10
    return rgb_clamped[0],rgb_clamped[1],rgb_clamped[2],EV


# Display on OLED
def displaynum(aperture,speed,iso,mode, isoadjust, lastmeasure, red, green, blue):
    #delta=-lastmeasure+sensorread()
    if mode=="AmbientAperture":
        textA=SSD.rgb(0,255,0)
        textT=SSD.rgb(255,255,255)
    else:
        textT=SSD.rgb(0,255,0)
        textA=SSD.rgb(255,255,255)
    ssd.fill(0)
    wri = CWriter(ssd,quantico40, fgcolor=textA,bgcolor=0, verbose=False)
    CWriter.set_textpos(ssd, 35,20)  # verbose = False to suppress console output
    try:
        wri.printstring(str(aperture))
    except:
        wri.printstring( "err")
    wrimem = CWriter(ssd,freesans20, fgcolor=textT,bgcolor=0, verbose=False)
    CWriter.set_textpos(ssd, 5,20)
    speed=str(speed)+" s"
    wrimem.printstring(speed)
    wrimem = CWriter(ssd,freesans20, fgcolor=SSD.rgb(255,255,255),bgcolor=0, verbose=False)
    CWriter.set_textpos(ssd, 35,0)  
    wrimem.printstring("F/")
    CWriter.set_textpos(ssd, 5,0)
    wrimem.printstring("T:")
    wrimem = CWriter(ssd,freesans20, fgcolor=SSD.rgb(55,55,55),bgcolor=0, verbose=False)    
    CWriter.set_textpos(ssd,105,80)
    wrimem = CWriter(ssd,freesans20, fgcolor=SSD.rgb(255,255,0),bgcolor=0, verbose=False)
    wrimem.printstring(str(iso))
    CWriter.set_textpos(ssd,105,0)
    wrimem = CWriter(ssd,freesans20, fgcolor=SSD.rgb(red,green,blue),bgcolor=0, verbose=False) # Colour of EV Number is the RGB code from the sensor
    wrimem.printstring(str(round(lastmeasure,1))+"EV") 
    if isoadjust:
        box=SSD.rgb(255,0,0)
    else:
        box=SSD.rgb(100,100,40)
    wrimem = CWriter(ssd,freesans20, fgcolor=0,bgcolor=box, verbose=False)
    CWriter.set_textpos(ssd,82,80)
    wrimem.printstring(" iso ")
    ssd.show()
    return

# Derive the appropriate stop value, based on the reading from the sensor and the chosen mode
def otherindex(index, isoindex, mode, lastmeasure):
    Eiso= lastmeasure + math.log2(float(isonum[isoindex]/100))
    if mode=="AmbientAperture":
        aperture=fstops[apertureindex]
        t= (float(aperture)**2)/(2**Eiso)
        #print(t)
        derivedindex = min(range(len(sspeed)), key=lambda i: abs(eval(sspeed[i])-t))
    elif mode=='AmbientShutterSpeed':
        speed=sspeed[speedindex]
        #print(eval(speed))
        N = math.sqrt(eval(speed)*2**(Eiso))
        #print(N)
        derivedindex = min(range(len(fstops)), key=lambda i: abs(float(fstops[i])-N))
    return derivedindex

    
# Hardware ################################################################################################
try:
    LIGHTSENSOR = {"sda": 4, "scl": 5}
    I2C = pimoroni_i2c.PimoroniI2C(**LIGHTSENSOR)
    bh1745 = breakout_bh1745.BreakoutBH1745(I2C)
    bh1745.leds(False)
except:
    splash("sensor?") # A visual cue that therehas been an issue with the sensor setup

# Pins Setup
pdc = Pin(20, Pin.OUT, value=0)                       # OLED DC
pcs = Pin(17, Pin.OUT, value=1)                       # OLED CS
prst = Pin(21, Pin.OUT, value=1)                      # OLED RST
psck = Pin(18)                                        # OLED SCK
pmosi = Pin(19)                                       # OLED MOSI
switch = Pin(15, mode=Pin.IN, pull = Pin.PULL_UP)     # inbuilt switch on the rotary encoder, ACTIVE LOW
modeswitch = Pin(8, mode=Pin.IN, pull = Pin.PULL_UP)  # 'mode' switch, the additional momentary switch
isoswitch = Pin(22, mode=Pin.IN, pull = Pin.PULL_UP)  # 'iso' switch, the additional momentary switch
outA = Pin(6, mode=Pin.IN)                            # Pin CLK of encoder
outB = Pin(7, mode=Pin.IN)                            # Pin DT of encoder
ledPin = Pin(25, mode = Pin.OUT, value = 0)           # Onboard led on GPIO 25

# Power Management
vsys = ADC(29)                                        # reads the system input voltage
charging = Pin(24, Pin.IN)                            # reading GP24 tells us whether or not USB power is connected
conversion_factor = 3 * 3.3 / 65535

full_battery = 4.2                  # these are our reference voltages for a full/empty battery, in volts
empty_battery = 2.8                 # the values could vary by battery size/manufacturer so you might need to adjust them

voltage = vsys.read_u16() * conversion_factor
percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))
if percentage > 100:
    percentage = 100

# setup screen
height = 128                         # the height of the oled
spi = SPI(0,
                  baudrate=10000000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=SPI.MSB,
                  sck=psck,
                  mosi=pmosi)
ssd = SSD(spi, pcs, pdc, prst, height)  # Create a display instance

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

# attach interrupt to the switch pin ( SW pin of mode switch )
modeswitch.irq(trigger = Pin.IRQ_FALLING ,
           handler = modebutton)

# attach interrupt to the switch pin ( SW pin of iso switch )
isoswitch.irq(trigger = Pin.IRQ_FALLING ,
           handler = isobutton)

# define global variables
outA_last = 0 # registers the last state of outA pin / CLK pin
outA_current = 0 # registers the current state of outA pin / CLK pin

button_last_state = False # initial state of encoder's button 
button_current_state = "" # empty string ---> current state of button
modebutton_last_state = False # initial state of encoder's button 
modebutton_current_state = "" # empty string ---> current state of button
isobutton_last_state = False # initial state of encoder's button 
isobutton_current_state = "" # empty string ---> current state of button

# Read the last state of CLK pin in the initialisaton phase of the program 
outA_last = outA.value() # lastStateCLK

# End Hardware ###################################################################################


# Main Logic
# Values for Fstop, Shutter Speed and ISO (ascending brightness)
fstops= [161, 144, 128, 114, 102, 90, 81, 72, 64, 57, 51, 45, 40, 36, 32, 29, 25, 22, 20, 18, 16, 14, 13, 11, 10, 9, 8, 7.1, 6.3, 5.6, 5, 4.5, 4, 3.6, 3.2, 2.8, 2.5, 2.2, 2, 1.8, 1.6, 1.4, 1.3, 1.1, 1, 0.9, 0.8, 0.7, 0.6]
sspeed= ["(1/ 8000)","(1/ 6400)","(1/ 5000)","(1/ 4000)","(1/ 3200)","(1/ 2500)","(1/ 2000)","(1/ 1600)","(1/ 1250)","(1/ 1000)","(1/ 800)","(1/ 640)","(1/ 500)","(1/ 400)","(1/ 320)","(1/ 250)","(1/ 200)", "(1/ 160)","(1/ 125)","(1/ 100)","(1/ 80)","(1/ 60)","(1/ 50)","(1/ 40)","(1/ 30)","(1/ 25)","(1/ 20)","(1/ 15)","(1/ 13)","(1/ 10)","(1/ 8)","(1/ 6)","(1/ 5)","(1/ 4)","0.3","0.4","0.5","0.6","0.8","1","1.3","1.6","2","2.5","3.2","4","5","6","8","10","13","15","20","25","30","40","50","60"]
isonum= [3,4,5,6,8,10,12,16,20,25,32,40,50,64,80,100,125,160,200,250,320,400,500,640,800,1000,1250,1600,2000,2500,3200, 4000, 5000,6400,8000]
modes= ["AmbientShutterSpeed","AmbientAperture"]
try:
    f = open('lastisoindex.txt', "r")
    isoindex = int(f.read())
    f.close()
except:
    print('no isoindex file..... using default')
    isoindex = 15                        # Default: ISO 100
evcorrection = 0                     # A stop adjustment for EV. Tweak this to calibrate if needed
                                     # (additive implies a proportional relationship between brightness and lux, check maths)
mode=modes[1]                        # Default: AmbientAperture mode
apertureindex = 26                   # Default: f/8 ('f8 and be there' - Weegee)
isoadjust=False
pin=0
counter= 0
lastcounter=0
lastupdate = utime.time()  
red, green, blue, lastmeasure=sensorread()
speedindex = otherindex(apertureindex, isoindex, mode, lastmeasure)
gc.enable()                          # enable garbage collection
refresh(ssd, True)                   # Initialise and clear display.
splash('photon')

while True:
    iso=isonum[isoindex]
    speed=sspeed[speedindex]
    aperture=fstops[apertureindex]
    encoder(pin)   
    if counter!=lastcounter or button_current_state != button_last_state:
    # adjust aperture or shutter speed, depending on mode selected
        if isoadjust:
            isoindex=isoindex + counter
            isoindex=max(0,isoindex)
            isoindex=min(len(isonum)-1,isoindex)
        if mode=="AmbientAperture":
            if not isoadjust:
                apertureindex=apertureindex + counter
                apertureindex=max(0,apertureindex)
                apertureindex=min(len(fstops)-1,apertureindex)
            # Now, derive shutter speed from aperture choice and lastmeasure
            speedindex = otherindex(apertureindex, isoindex, mode, lastmeasure)
        elif  mode=='AmbientShutterSpeed':
            if not isoadjust:
                speedindex=speedindex + counter
                speedindex=max(0,speedindex)
                speedindex=min(len(sspeed)-1,speedindex)
            # Now, derive aperture from shutter speed choice and lastmeasure
            apertureindex = otherindex(speedindex, isoindex, mode, lastmeasure)
        counter=0
        displaynum(aperture, speed, iso,mode, isoadjust,lastmeasure, red,green,blue)
    lastcounter=counter
    button_last_state = False     # reset button last state to false again ,
                                  # can also be done from other subroutines
                                  # or from the main loop
    modebutton_last_state = False # see above
    isobutton_last_state = False  # see above
    gc.collect()                  # force garbage collect
    now = utime.time()
