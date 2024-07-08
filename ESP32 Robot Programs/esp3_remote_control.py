import machine
import espnow
import network
import _thread
from Button import Button

# =========== CONECTION FOR THE ESP32 3 ===========================================
sta = network.WLAN(network.STA_IF)
sta.active(True)
esp = espnow.ESPNow()
esp.active(True)

peer_esp2 = b'\xd4\x8a\xfc\x9d\xa6\x88' # MAC address of the ESP32 2 --- Contains the rails
peer_esp1 = b'\x08\xd1\xf93h\xe8'       # MAC address of the ESP32 1 --- Contains the Car
peer_esp4 = b'\xecd\xc9\x82x\xd4'       # MAC address of the ESP32 4 --- Contains the arnes
peer_esp5 = b'\xa0\xa3\xb3)B\x0c'       # MAC address of the ESP32 5 --- Contains the horizontal sensors

esp.add_peer(peer_esp1)
esp.add_peer(peer_esp2)
esp.add_peer(peer_esp4)
esp.add_peer(peer_esp5)

# =============PIN SETUP ================================================================
pinBlueLED = 23  # Blue LED indicates that we are in the Manual mode
pinGreenLED = 22 # Green LED inidicates that we are in the Auto mode

manualLED = machine.Pin(pinBlueLED, machine.Pin.OUT)
autoLED = machine.Pin(pinGreenLED, machine.Pin.OUT)

# ============== THREADS ==================================================
def reciveMode(): # This recives a messages from ESP32 5 when the cleaning routine has finished
    while True:
        _, msg = esp.recv()
        if msg:
            Button.modo = msg.decode()
            
_thread.start_new_thread(reciveMode, [])

if __name__ == '__main__':
    #  =========== CREATING THE BUTTONS OBJECTS ==============================
    right = Button(19, "Right", "Stop", peer_esp2)
    left = Button(18, "Left", "Stop", peer_esp2)
    
    up = Button(21, "Up", "Stop", peer_esp4, peer_esp1)
    down = Button(4, "Down", "Stop", peer_esp4, peer_esp1)
    
    activate = Button(33, "Activate", "Desactivate", peer_esp1)
    
    upSys = Button(34, "UpSys", "", peer_esp1)
    downSys = Button(13,"DonSys", "", peer_esp1)
    
    auto = Button(25, "Auto", "Manual", peer_esp5)
    stop = Button(26, "Stop", "Stop", peer_esp4, peer_esp2, peer_esp1, peer_esp5)

    while (True):
        # Reads the state of the buttons
        right.reading()
        left.reading()
        
        up.reading()
        down.reading()
        
        activate.reading()
        
        upSys.reading()
        downSys.reading()
        
        auto.reading()
        stop.reading()
        
        # Change the mode and the LED
        if Button.modo == 'Manual':
            manualLED.value(1)
            autoLED.value(0)
        elif Button.modo == 'Auto':
            autoLED.value(1)
            manualLED.value(0)