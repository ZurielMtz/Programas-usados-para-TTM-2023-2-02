import network
import espnow
# This program recives msg from IHM (ESP32 3)
# Upload this program to the ESP32 that you want to recive the messages


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)

# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

if __name__ == '__main__':
    while True:
        _, msg = esp.recv()
        print(msg) 
