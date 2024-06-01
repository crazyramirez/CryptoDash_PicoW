from machine import Pin, SPI
import network
import socket
import urequests as requests
from ili934xnew import ILI9341, color565
from time import sleep
import tt32
import tt14
import json
import machine

# TFT screen pins configuration
TFT_CLK_PIN = 10  # SCK
TFT_MOSI_PIN = 11  # MOSI
TFT_MISO_PIN = 12  # MISO (if used)
TFT_CS_PIN = 13  # Chip Select
TFT_RST_PIN = 15  # Reset
TFT_DC_PIN = 14  # Data/Command
TFT_LED_PIN = 9  # LED

# TFT screen configuration
spi = SPI(1, baudrate=32000000, polarity=0, phase=0, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN), miso=Pin(TFT_MISO_PIN))
display = ILI9341(spi, cs=Pin(TFT_CS_PIN), dc=Pin(TFT_DC_PIN), rst=Pin(TFT_RST_PIN), w=320, h=320, r=0)  # 90-degree rotation

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
        sleep(1)
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
    display.set_font(tt32)
    display.set_pos(10, 10)
    display.write("Network: CryptoDash")
    display.set_pos(10, 40)
    display.write("Password: 12345678")
    display.set_pos(10, 90)
    display.write("Connect and visit:")
    display.set_pos(10, 120)
    display.write("http://192.168.4.1")

# Configuration HTML page
config_page = """
<!DOCTYPE html>
<html>
<head>
    <title>WiFi Config</title>
</head>
<body>
    <h1>WiFi Config</h1>
    <form action="/configure" method="post">
        SSID: <input type="text" name="ssid"><br>
        Password: <input type="text" name="password"><br>
        <input type="submit" value="Submit">
    </form>
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
def display_crypto_data(y, name, symbol, price, change):
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
                    sleep(3)
                    machine.reset()
                else:
                    response = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\nInvalid Request'
            else:
                response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nPage not found'
            
            cl.send(response)
            cl.close()

# Main function
def main():
    init_wifi()
    crypto_list = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('ADA', 'Cardano'),
        ('BNB', 'Binance Coin'),
        ('SOL', 'Solana')
    ]
    while True:
        display.fill_rectangle(0, 0, display.width, display.height, color565(0, 0, 0))
        y = 10
        for symbol, name in crypto_list:
            price, change = fetch_crypto_data(symbol)
            if price is not None and change is not None:
                display_crypto_data(y, name, symbol, price, change)
            y += 62  # Space between cryptocurrencies
        sleep(120)

if __name__ == '__main__':
    main()
