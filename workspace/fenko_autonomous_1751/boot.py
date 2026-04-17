import machine  # type: ignore
import network  # type: ignore
from time import sleep

# WiFi credentials
SSID = "your_ssid"
PASSWORD = "your_password"

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    pass

print("Connected to WiFi")

# Set up PINS
led = machine.Pin(25, machine.Pin.OUT)


# Function to toggle LED
def toggle_led():
    led.value(not led.value())


# Main loop
try:
    while True:
        toggle_led()
        sleep(1)
except KeyboardInterrupt:
    pass

wlan.disconnect()
machine.reset()
