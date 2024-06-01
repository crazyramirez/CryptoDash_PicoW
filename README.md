# CRYPTO DASHBOARD - Raspberry Pi Pico W
Simple but beautiful Cryptocurrency Dashboard using the Binance API.
<br><br>
**Developed in MicroPython for Raspberry Pi Pico W**
<br><br>
Integrated support for 2.8" TFT LCD display (ili9341), driver included with simple sources.
<br><br>
In this mini app you have everything you need to configure the wifi connection of your RPi Pico W through an Access Point from another device.
<br><br>
And of course the simple Crypto Dashboard adapted to the ili9341 screen

## INSTALL
In this case I'm using the RPi Pico W board, so you need to download the corresponding Firmware:
<br>
**https://rpf.io/pico-w-firmware**
<br><br>
First of all, have the Pico W disconnected.
Then hold down the BOOTSEL button on your Pico W while connecting it to the computer via USB.
A drive will appear on the computer, copy the downloaded Firmware file to the main directory, the device will reboot.
<br><br>
Now it's time to open your favorite MicroPython editor, in my case I like Thonny, since it's easy and efficient.
In Thonny go to Run-->Configure Interpreter
And select MicroPhyton (Raspberry Pi Pico)
<br><br>
Download the files from this repository and copy them to the root of your device using your code editor.
<br><br>
## ALL SET
Now you just have to RUN your code.
<br><br>
The main file "main.py" includes the code, in just over 200 lines you have everything you need to configure your device's wifi using an Access Point and the simple viewer to display the price of 5 cryptocurrencies adapted to the ili9341 screen.
<br><br>
If you have another screen model you simply have to find the appropriate drivers and configure the parameters in main.py (TFT screen configuration)
<br><br>
