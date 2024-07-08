import machine
import utime
import espnow
import network
import time
import _thread
from LimitSensor import LimitSensor

# =========== CONEXION A LA ESP32 1 ===========================================
sta = network.WLAN(network.STA_IF) 
sta.active(True)
# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

peer_esp2 = b'\xd4\x8a\xfc\x9d\xa6\x88' # MAC address of ESP32 2 ---- Contians the rail
peer_esp4 = b'\xecd\xc9\x82x\xd4'       # MAC address of ESP32 4 ---- Contians the arnes
peer_esp1 = b'\x08\xd1\xf93h\xe8'       # MAC address of ESP32 1 ---- Contians the car
peer_esp3 = b"\xe4e\xb8'G\xb0"          # MAC address of ESP32 3 ---- Contians the IHM
# Add peers to the ESP32 5
esp.add_peer(peer_esp2) 
esp.add_peer(peer_esp1)
esp.add_peer(peer_esp3)
esp.add_peer(peer_esp4)

# ==== SELECT MODE ==================================
mode = 'Manual' # Mode that we're working, there are two modes Manual and Auto
last_flag = False # This flag indictes if we are in the last cycle -- False: We are not in the last cycle
def select():
    global mode, last_flag
    while True:
        _, msg = esp.recv() # Recives the message from ESP32 3 and ESP32 5
        if msg:
            mode = msg.decode()
            print(mode) 
            if mode == 'Last': # If we are in the last cycle we change the flag
                last_flag = True
                mode ='Auto'

_thread.start_new_thread(select,[])

if __name__ == '__main__':
    state = 'Return' # Defines the states for the automatic rutine
    # PIN SETUP
    rightSensor = LimitSensor(5,"StopR",esp,"Free",'Prepare','Return',peer_esp2) 
    leftSensor = LimitSensor(17,"StopL", esp, "Free",'Next','Prepare', peer_esp2)
    while True:
        if mode == 'Manual': # For manual mode, ESP32 5 only reads the sensors state
            rightSensor.readManual()
            leftSensor.readManual()    
            
        elif (mode == 'Auto'): # For auto mode, ESP32 5 has the control to send messages to the rest of the ESP32
            state = 'Return'
            while(mode == 'Auto'): # Starts the rutine
                if state =='Return': # Moves the robot to the right side of the solar panels
                    if LimitSensor.bandera_enviado == False: # Only send once the message Right
                        time.sleep(6)
                        esp.send(peer_esp2, "Right") # Send the message Right to ESP32 2
                        LimitSensor.bandera_enviado = True
                        
                    state = rightSensor.readAuto() # Reads the state of the horizontal sensor
                    # and the return value gives us the next state of the rutine
                
                if state == 'Prepare': # Prepare the cleaning system
                    if LimitSensor.bandera_enviado == False:
                        time.sleep(6)
                        esp.send(peer_esp1, 'DownSys') # Move down the cleaning system
                        time.sleep(6)
                        esp.send(peer_esp1, 'Activate') # Actives the brush
                        time.sleep(6)
                        LimitSensor.bandera_enviado = False # Prepare the flag for the next step
                        state = 'Cleaning' # Change to the next state
                
                if state == 'Cleaning': # Cleaning state, moves the robot to the left while the brush is spinning
                    if LimitSensor.bandera_enviado == False: # Only send once the message Let
                        esp.send(peer_esp2, 'Free') # Free the flags for the left and right sensors
                        esp.send(peer_esp2, 'Left') # Send the message Left to ESP32 2
                        LimitSensor.bandera_enviado = True 
                    state = leftSensor.readAuto() # Reads the state of the horizontal sensor

                if state == 'Next': # Prepare the next cycle
                    if LimitSensor.bandera_enviado == False:
                        time.sleep(3)
                        esp.send(peer_esp1, 'Desactivate') # Desactivates the brush
                        time.sleep(3)
                        esp.send(peer_esp1,'UpSys') # Move up the cleaning system
                        time.sleep(3)
                        esp.send(peer_esp4, 'Down') # Move the pulley to move down the car
                        esp.send(peer_esp1, 'Down') # Move the car down 
                        state = 'Return' # Prepare the next state
                        LimitSensor.bandera_enviado = False
                        esp.send(peer_esp1, 'Free') # Free the flags for the horizontal sensors
                        
                    if last_flag == True: # If we are in the last cycle and we finished cleaining we move up the car
                        time.sleep(2)
                        esp.send(peer_esp4,'UpCar') # Moves the pulley up
                        esp.send(peer_esp1,'UpCar') # Moves the car up
                        mode = 'Manual' # Changes the mode
                        state = 'Last' # Change the state
                        esp.send(peer_esp3, mode) # Gives the control to the IHM
                        last_flag = False # Reset the flag of last cycle
                
                if state == 'Last':
                    break
                
        elif(mode == 'Stop'): # If we revice the stop emergency from ESP32 3 we stop everything
            esp.send(peer_esp1, 'Stop')
            esp.send(peer_esp2, 'Stop')
            esp.send(peer_esp2, 'Desactivate')
            esp.send(peer_esp4, 'Stop')
            esp.send(peer_esp3, 'Manual')