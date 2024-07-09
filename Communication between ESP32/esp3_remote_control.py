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
# Chage the MAC address of the ESP32 that you are working, if you don't have it
# use the program called: find_mac_addr.py to find the MAC address of the ESP32
peer_esp2 = b'\xd4\x8a\xfc\x9d\xa6\x88' 
peer_esp1 = b'\x08\xd1\xf93h\xe8'       
peer_esp4 = b'\xecd\xc9\x82x\xd4'       
peer_esp5 = b'\xa0\xa3\xb3)B\x0c'       

esp.add_peer(peer_esp1)
esp.add_peer(peer_esp2)
esp.add_peer(peer_esp4)
esp.add_peer(peer_esp5)
esp.add_peer(peer_esp1)

# =============PIN SETUP ================================================================
pinBlueLED = 23  # Blue LED indicates that we are in the Manual mode
pinGreenLED = 22 # Green LED inidicates that we are in the Auto mode


# ============== THREADS ==================================================
def reciveMode(): # This recives a messages from ESP32 5 when the cleaning routine has finished
    while True:
        _, msg = esp.recv()
        if msg:
            Button.modo = msg.decode()
            
_thread.start_new_thread(reciveMode, [])

if __name__ == '__main__':
    #  =========== CREATING THE BUTTONS OBJECTS ==============================
    # Change the peer esp32 to see the msgs that can and cannot recive
    right = Button(19, "Right", "Stop", peer_esp1)
    left = Button(18, "Left", "Stop", peer_esp1)
    
    up = Button(21, "Up", "Stop", peer_esp2)
    down = Button(4, "Down", "Stop", peer_esp2)
    
    activate = Button(33, "Activate", "Desactivate", peer_esp1)
    
    upSys = Button(34, "UpSys", "", peer_esp4)
    downSys = Button(13,"DonSys", "", peer_esp4)
    
    auto = Button(25, "Auto", "Manual", peer_esp1)
    stop = Button(26, "Stop", "Stop", peer_esp1)

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