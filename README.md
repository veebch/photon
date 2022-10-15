![Action Shot](/images/actionshot1.jpg)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)

# Photon: an open-source incident light meter 

Photon reproduces the some of the functionality of more expensive tools, using a few inexpensive/readily available parts. It measures light brightness, as well as the red, green and blue components of the light. There is soldering involved, but don't let that put you off, [it's easy](https://www.youtube.com/watch?v=Qps9woUGkvI).

## Background

An incident light-meter can be an essential tool in photography (especially film photography with old cameras). The sophisticated computation baked-in to modern cameras devotes a lot of effort guessing 'how much light is falling on the subject?". If you have the option of getting to the subject and taking a reading, no guessing is required and everything becomes a lot easier. 

## Components

- Raspberry Pi Pico
- OLED Screen                 (Waveshare 120x120 full colour)
- LiPo Power shim             ([Pimoroni](https://shop.pimoroni.com/products/pico-lipo-shim?variant=32369543086163)... Sheffield massive represent)
- Rotary encoder              (adjust settings and change priority mode)
- Two momentary switches      (1x[keyboard switch](https://keyboardsexpert.com/types-of-keyboard-switches/) and 1x 6x6mm microswitch to measure light and set iso adjust mode respectively)
- Light Sensor                (Pimoroni BH1745)             
- LiPo/LiIon battery



# Assembly

## Hardware

Solder the power shim to the pico. Connect the Lipo/LiIon battery to the shim. Then connect the rest of the components to the GPIO pins as follows.

### Light Sensor

| [Pico GPIO](https://www.elektronik-kompendium.de/sites/raspberry-pi/bilder/raspberry-pi-pico-gpio.png) | BH1745 |
|-----------|------|
|   4       | SDA  |
|   5      | SCL  |


### OLED

| [Pico GPIO](https://www.elektronik-kompendium.de/sites/raspberry-pi/bilder/raspberry-pi-pico-gpio.png) | OLED |
|-----------|------|
|   19       | DIN/MOSI  |
|   18      | CLK/SCK  |
|   17      | CS  |
|   20       | DC  |
|   21      | RST  |


### Rotary Encoder:

| [Pico GPIO](https://www.elektronik-kompendium.de/sites/raspberry-pi/bilder/raspberry-pi-pico-gpio.png) | Rotary Encoder |
|-----------|----------------|
|   6       | CLK            |
|   7        | DT             |
|   8       | SW             |

### Switches

| [Pico GPIO](https://www.elektronik-kompendium.de/sites/raspberry-pi/bilder/raspberry-pi-pico-gpio.png) | Switches |
|-----------|----------------|
|   15       |       Measure      |
|   22       |       ISO     |


Once you've tested that things are working, squeeze the parts into an enclosure. If you have access to a 3D printer, there are stl files in the `cases` directory.

## Software

Download a `uf2` image from the [Pimoroni github repository](https://github.com/pimoroni/pimoroni-pico/releases) and install it on the Pico according to the instructions. You need to use the Pimoroni image to be able to use Pimoroni drivers for the light sensor.

Clone this repository to your computer using the commands (from a terminal)

```
cd ~
git clone https://github.com/veebch/photon.git
cd photon
```

Copy the contents to the repository using [ampy](https://pypi.org/project/adafruit-ampy/) and the commands.
```
sudo ampy -p /dev/ttyACM0 put drivers
sudo ampy -p /dev/ttyACM0 put gui
sudo ampy -p /dev/ttyACM0 put color_setup.py
sudo ampy -p /dev/ttyACM0 put main.py
```

Done! All the required files should now be on the Pico. When you disconnect from USB and power on using the button on the power shim the script will autorun.

# Contributing to the code

If you look at this, find it interesting, and know you can make it better then please fork the repository and use a feature branch. Pull requests are welcome and encouraged.

If you have some photography expertise that you think could be embedded in the code then raise an issue on GitHub or mail us.

# Appendix
## Derived formulas

The simple calculations that lead to a reading are based on the Wikipedia entry on [exposure value](https://en.wikipedia.org/wiki/Exposure_value).

The brightness value returned by the Pimoroni BH1745 (lx) is converted to an exposure value ( $E_v$ ) for ISO 100. This exposure value is then adjusted to an Exposure value for the chosen ISO ( $E_{ISO}$ ) using

$$E_{ISO}=E_v + \log_2 {{ISO}\over{100}}.$$

Then, depending on the priority on the light meter, the remaining value is calculated using

$$t = {{N^2} \over {2^{E_{ISO}}}}$$  

or

$$N = \sqrt{t 2^{ E_{ISO}}}$$

where $t$ is shutter speed and $N$ is f-stop. The value is then rounded to the nearest nominal value and displayed on the screen.

End of maths.

## Video

A real-world test

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/xju3yHBka7Q/0.jpg)](https://www.youtube.com/watch?v=xju3yHBka7Q)



## To Do

- Power management
- Flash measurement (add integrator circuit?)
- Assembly Instructions
- Calibration via GUI
