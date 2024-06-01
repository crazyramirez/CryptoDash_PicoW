from machine import Pin, SPI, Timer
import network
import socket
import urequests as requests
from ili934xnew import ILI9341, color565
import time
import tt32
import tt24
import tt14
import json
import machine
import os

# TFT screen pins configuration
TFT_CLK_PIN = 10  # SCK
TFT_MOSI_PIN = 11  # MOSI
TFT_MISO_PIN = 12  # MISO (if used)
TFT_CS_PIN = 13  # Chip Select
TFT_RST_PIN = 15  # Reset
TFT_DC_PIN = 14  # Data/Command
TFT_LED_PIN = 9  # LED

# Configure the button pin with a pull-down resistor
BUTTON_PIN = 17  # Button connected to GPIO 17
LONG_PRESS_TIME = 3000  # Long press time in milliseconds
button_pressed_time = 0
button_released_time = 0
button_state = "idle"

# TFT screen configuration
spi = SPI(1, baudrate=128000000, polarity=0, phase=0, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN), miso=Pin(TFT_MISO_PIN))
display = ILI9341(spi, cs=Pin(TFT_CS_PIN), dc=Pin(TFT_DC_PIN), rst=Pin(TFT_RST_PIN), w=320, h=240, r=0)  # 90-degree rotation

# Configure the LED pin
led = Pin(TFT_LED_PIN, Pin.OUT)
led.value(1)  # Turn on the backlight

# Save Wi-Fi credentials to a file
def save_credentials(ssid, password):
    credentials = {'ssid': ssid, 'password': password}
    with open('wifi_credentials.json', 'w') as f:
        json.dump(credentials, f)

# Load Wi-Fi credentials from a file
def load_credentials():
    try:
        with open('wifi_credentials.json', 'r') as f:
            credentials = json.load(f)
        return credentials['ssid'], credentials['password']
    except OSError:
        return None, None

# Save tokens to a file
def save_tokens(tokens):
    with open('tokens.json', 'w') as f:
        json.dump(tokens, f)

# Load tokens from a file
def load_tokens():
    default_tokens = ["BTC", "ETH", "ADA", "BNB", "SOL"]
    try:
        # Try to open the file in read mode
        with open('tokens.json', 'r') as f:
            tokens = json.load(f)
        # If the file is empty or invalid JSON, this will raise an exception
        if not tokens:
            raise ValueError("Empty file or invalid JSON")
        return tokens
    except (OSError, ValueError):
        # If the file does not exist, is empty, or contains invalid JSON, create it with default tokens
        with open('tokens.json', 'w') as f:
            json.dump(default_tokens, f)
        return default_tokens

# URL-decode function
def url_decode(value):
    hex_values = {
        '%20': ' ', '%21': '!', '%22': '"', '%23': '#', '%24': '$', '%25': '%', '%26': '&', '%27': "'",
        '%28': '(', '%29': ')', '%2A': '*', '%2B': '+', '%2C': ',', '%2D': '-', '%2E': '.', '%2F': '/',
        '%30': '0', '%31': '1', '%32': '2', '%33': '3', '%34': '4', '%35': '5', '%36': '6', '%37': '7',
        '%38': '8', '%39': '9', '%3A': ':', '%3B': ';', '%3C': '<', '%3D': '=', '%3E': '>', '%3F': '?',
        '%40': '@', '%41': 'A', '%42': 'B', '%43': 'C', '%44': 'D', '%45': 'E', '%46': 'F', '%47': 'G',
        '%48': 'H', '%49': 'I', '%4A': 'J', '%4B': 'K', '%4C': 'L', '%4D': 'M', '%4E': 'N', '%4F': 'O',
        '%50': 'P', '%51': 'Q', '%52': 'R', '%53': 'S', '%54': 'T', '%55': 'U', '%56': 'V', '%57': 'W',
        '%58': 'X', '%59': 'Y', '%5A': 'Z', '%5B': '[', '%5C': '\\', '%5D': ']', '%5E': '^', '%5F': '_',
        '%60': '`', '%61': 'a', '%62': 'b', '%63': 'c', '%64': 'd', '%65': 'e', '%66': 'f', '%67': 'g',
        '%68': 'h', '%69': 'i', '%6A': 'j', '%6B': 'k', '%6C': 'l', '%6D': 'm', '%6E': 'n', '%6F': 'o',
        '%70': 'p', '%71': 'q', '%72': 'r', '%73': 's', '%74': 't', '%75': 'u', '%76': 'v', '%77': 'w',
        '%78': 'x', '%79': 'y', '%7A': 'z', '%7B': '{', '%7C': '|', '%7D': '}', '%7E': '~'
    }
    for hex_val, char in hex_values.items():
        value = value.replace(hex_val, char)
    return value

# Connect to Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() == network.STAT_GOT_IP:
            print('Connected to WiFi:', wlan.ifconfig())
            return True
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)
    print('Could not connect to WiFi')
    return False

# Start in AP mode
def start_ap_mode():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid='CryptoDash', password='123456789')
    ap.active(True)
    print('Access Point started, connect to: CryptoDash with password: 123456789')
    display_ap_info()
    return ap

# Display connection information on TFT screen
def display_ap_info():
    display.fill_rectangle(0, 0, display.width, display.height, color565(0, 0, 0))  # Clear screen
    display.set_font(tt24)
    display.set_pos(10, 10)
    display.write("Network: CryptoDash")
    display.set_pos(10, 40)
    display.write("Password: 123456789")
    display.set_pos(10, 90)
    display.write("Connect and visit:")
    display.set_pos(10, 120)
    display.set_color(color565(255, 255, 255), color565(0, 0, 255))
    display.write("http://192.168.4.1")

# Configuration HTML page
config_page = """



<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" name="viewport"/>
    <title>WiFi Config</title>
    <style>
        html {
            width: 100vw;
            height: 100vh;
            background: linear-gradient(45deg, #4e54c8, #d1d3ff);
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
        }
        body {
            font-family: Arial, sans-serif;
            background-color: transparent;
            display: flex;
            justify-content: center;
            align-items: center;
            user-select: none;
            -webkit-user-select: none;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 320px;
            margin-top: 30px;
        }
        h2, h5 {
            text-align: center;
            color: #333333;
        }
        .input-container {
            margin: 10px 0px 20px;
            border-radius: 5px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #797979;
            background-color: transparent;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            border: none;
            border-radius: 5px;
            box-sizing: border-box;
            background-color: #e9e9e9;
        }
        input[type="submit"] {
            width: 100%;
            padding: 10px;
            background-color: #4CAF50;
            border: none;
            border-radius: 5px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            fetch('tokens.json')
                .then(response => response.json())
                .then(data => {
                    if (Array.isArray(data)) {
                        document.getElementById('crypto1').value = data[0] || '';
                        document.getElementById('crypto2').value = data[1] || '';
                        document.getElementById('crypto3').value = data[2] || '';
                        document.getElementById('crypto4').value = data[3] || '';
                        document.getElementById('crypto5').value = data[4] || '';
                    }
                })
                .catch(error => console.error('Error loading tokens.json:', error));
        });
    </script>
</head>
<body>
    <div class="container">
        <h2>WiFi Config</h2>
        <h5>Leave it empty if you're connected</h5>
        <form action="/configure" method="post">
            <div class="input-container">
                <label for="ssid">SSID</label>
                <input type="text" id="ssid" name="ssid">
            </div>
            <div class="input-container">
                <label for="password">PASSWORD</label>
                <input type="text" id="password" name="password">
            </div>
            <h2>Cryptocurrencies</h2>
            <h5>Use Symbol (BTC, ETH, ADA...)</h5>
            <div class="input-container">
                <label for="crypto1">Cryptocurrency 1</label>
                <input type="text" id="crypto1" name="crypto1" placeholder="Default Value BTC">
            </div>
            <div class="input-container">
                <label for="crypto2">Cryptocurrency 2</label>
                <input type="text" id="crypto2" name="crypto2" placeholder="Default Value ETH">
            </div>
            <div class="input-container">
                <label for="crypto3">Cryptocurrency 3</label>
                <input type="text" id="crypto3" name="crypto3" placeholder="Default Value ADA">
            </div>
            <div class="input-container">
                <label for="crypto4">Cryptocurrency 4</label>
                <input type="text" id="crypto4" name="crypto4" placeholder="Default Value BNB">
            </div>
            <div class="input-container">
                <label for="crypto5">Cryptocurrency 5</label>
                <input type="text" id="crypto5" name="crypto5" placeholder="Default Value SOL">
            </div>
            <input type="submit" value="SUBMIT">
        </form>
    </div>
</body>
</html>
"""

# Handle Wi-Fi configuration
def handle_configure(request):
    headers, body = request.split('\r\n\r\n')
    if 'POST /configure' in headers:
        params = body.split('&')
        ssid = url_decode(params[0].split('=')[1])
        password = url_decode(params[1].split('=')[1])
        
        crypto1 = url_decode(params[2].split('=')[1]).upper() if params[2].split('=')[1] else 'BTC'
        crypto2 = url_decode(params[3].split('=')[1]).upper() if params[3].split('=')[1] else 'ETH'
        crypto3 = url_decode(params[4].split('=')[1]).upper() if params[4].split('=')[1] else 'ADA'
        crypto4 = url_decode(params[5].split('=')[1]).upper() if params[5].split('=')[1] else 'SOL'
        crypto5 = url_decode(params[6].split('=')[1]).upper() if params[6].split('=')[1] else 'BNB'
        
        tokens = [crypto1, crypto2, crypto3, crypto4, crypto5]
        save_tokens(tokens)
        return ssid, password
    return None, None


# Fetch cryptocurrency data
def fetch_crypto_data(symbol):
    try:
        url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT'
        response = requests.get(url)
        data = response.json()
        price = float(data['lastPrice'])
        change = float(data['priceChangePercent'])
        return price, change
    except Exception as e:
        print(f'Error fetching data for {symbol}:', e)
        return None, None

# Format price with commas
def format_price(price):
    price_str = '{:.2f}'.format(price)
    integer_part, decimal_part = price_str.split('.')
    integer_part_reversed = ''.join(reversed(integer_part))
    chunks = [integer_part_reversed[i:i+3] for i in range(0, len(integer_part_reversed), 3)]
    integer_part_with_commas = ''.join(reversed(','.join(chunks)))
    return '{}.{}'.format(integer_part_with_commas, decimal_part)

# Display cryptocurrency data on TFT screen
def display_crypto_data(y, symbol, price, change):
    display.set_font(tt32)
    display.set_pos(10, y)
    formatPrice = format_price(price)
    display.write(f'{symbol}: {formatPrice} $')
    display.set_pos(10, y + 32)
    display.set_font(tt14)
    change_color = color565(0, 255, 0) if change >= 0 else color565(255, 0, 0)
    display.set_color(change_color, color565(0, 0, 0))
    display.write(f'24h Change: {change:.2f}%')
    display.set_color(color565(255, 255, 255), color565(0, 0, 0))  # Reset color


# Initialize Wi-Fi or start AP mode if no connection
def init_wifi():
    ssid, password = load_credentials()
    if ssid and password and connect_wifi(ssid, password):
        return
    else:
        enter_ap_mode()

# Function to enter AP mode
def enter_ap_mode():
    ap = start_ap_mode()
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024).decode('utf-8')
        print('Request:', request)
        response = ""

        if 'GET / ' in request:
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + config_page
        elif 'POST /configure' in request:
            ssid, password = handle_configure(request)
            if ssid and password:
                save_credentials(ssid, password)
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nConfiguration saved. Rebooting...'
            cl.send(response)
            cl.close()
            time.sleep(3)
            machine.reset()
        else:
            response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nPage not found'
        
        cl.send(response)
        cl.close()

# Remove Credentials
def remove_credentials():
    try:
        # Remove the credentials file
        os.remove('wifi_credentials.json')
        os.remove('tokens.json')  # Eliminar también los tokens
        print("Credentials and tokens file removed")
    except Exception as e:
        print("Failed to remove credentials or tokens file:", e)
    # Restart the device
    time.sleep(1)
    machine.reset()

# Function to fetch and display cryptocurrency data
def fetch_and_display_crypto_data():
    tokens = load_tokens()

    display.fill_rectangle(0, 0, display.width, display.height, color565(0, 0, 0))
    y = 10
    for symbol in tokens:
        price, change = fetch_crypto_data(symbol)
        if price is not None and change is not None:
            display_crypto_data(y, symbol, price, change)
        y += 62  # Space between cryptocurrencies

def single_press_action():
    print("Single press detected - Fetch Data")
    fetch_and_display_crypto_data()
    time.sleep(1)

def long_press_action():
    print("Long press detected - Enter AP Mode")
    enter_ap_mode()

def handle_button(pin):
    global button_pressed_time, button_released_time, button_state
    if pin.value() == 0:  # Button pressed
        button_pressed_time = time.ticks_ms()
        button_state = "pressed"
    else:  # Button released
        button_released_time = time.ticks_ms()
        if button_state == "pressed":
            press_duration = time.ticks_diff(button_released_time, button_pressed_time)
            if press_duration > LONG_PRESS_TIME:
                long_press_action()
            else:
                single_press_action()
        button_state = "idle"

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP) 
button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_button)

# Main function
def main():
    tokens = load_tokens()
    ssid, password = load_credentials()
    time.sleep(2)
    init_wifi()    
    while True:
        # Fetch and display data initially
        fetch_and_display_crypto_data()
        time.sleep(600)
        
if __name__ == '__main__':
    main()
