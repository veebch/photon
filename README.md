[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

# Incident

An open-source light-meter that reproduces the functionality of more expensive tools, using a few inexpensive/readily available parts. There is soldering involved, but don't let that put you off.

# Background

An incident light-meter is an essential tool in photography. The sophisticated computation baked-in to modern cameras devotes a lot of effort guessing 'how much light is falling on the subject?". If you have the option of getting to the subject and taking a reading, everything becomes a lot easier. 

# Hardware

- Raspberry Pi Pico                     
- Rotary encoder              (adjust settings and measure)
- 2x Momentary switch         (to toggle mode and iso)
- Pimoroni BH1745             (Sheffield massive represent)
- LiPo battery
- PIR Dome

# Installation

Download a `uf2` image from [pimoroni](https://github.com/pimoroni/pimoroni-pico/releases)

# Calculating

The simple calculations that lead to a reading are based on the Wikipedia entry on [exposure value](https://en.wikipedia.org/wiki/Exposure_value).

The ADC value measured by the Pico is converted to an exposure value ($E_v$) by using a fitted line that gives exposure value as a function of the ADC value. This exposure value is then adjusted to an Exposure value for the chosen ISO ($E_{ISO}$) using

$$E_{ISO}=E_v + \log_2 {{ISO}\over{100}}.$$

Then, depending on the priority on the light meter, the remaining value is calculated using

$$t = {{N^2} \over {2^{E_{ISO}}}}$$  

or

$$N = \sqrt{t 2^{ E_{ISO}}}$$

where $t$ is shutter speed and $N$ is f-stop. The value is then rounded to the nearest nominal value and displayed on the screen End of maths.


# To Do

- Power management
- Flash measurement (add integrator circuit?)
