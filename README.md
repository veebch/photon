[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

# Incident

An open-source light-meter that reproduces the functionality of expensive tools, using a few inexpensive/readily available parts. There is a whisper of soldering involved in this but don't let that put you off.


# Background

An incident light-meter is an essential tool in photography. The sophisticated computation baked-in to modern cameras devotes a lot of effort guessing 'how much light is falling on the subject?". If you have the option of getting to the subject and taking a reading, everything becomes a lot easier.


# Hardware

- A Pi Pico                     
- A Rotary Encoder              (adjust settings and measure)
- A Momentary Switch            (to toggle mode)
- A Photodiode                  (fast and accurate measurement in case we end up writing code that is clever enough to measure studio flash)            
- A LiPo Battery
- A roll-on Deodorant bottle
- A 3d printed insert for said deodorant bottle

# Calculating Values

The ADC value is converted to an Exposure value ($E_v$). This Exposure value is then adjusted to and Exposure value for the chosen ISO.
Then depending on the priority on the light meter, the remaining value is calculated.



# To Do

- Power management. Power down after delay? Accelerometer activated oled? Battery indicator? 
- Flash measurement.
