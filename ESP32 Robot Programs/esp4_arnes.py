import machine
import time
import _thread
import espnow
import network
from math import pi
from Arnes import Arnes
from PinMotorArnes import PinMotorArnes

# Limit sensors
upper_sensor = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_DOWN) 
lower_sensor = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_DOWN)

Tm = 0.05 # Sampling time in SECONDS ****

# =========== CONECTION FOR THE ESP32 4 ===========================================
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)
peer_esp1 = b'\x08\xd1\xf93h\xe8' # MAC address of ESP32 1 ---- Contians the car
peer_esp5 = b'\xa0\xa3\xb3)B\x0c' # MAC address of ESP32 5 --- Feedback for the ESP32 5

# Add peers to the ESP32 4
esp.add_peer(peer_esp1) 
esp.add_peer(peer_esp5)

# ============= THREADS =======================
# ========= MOVING THE PULLEY ======================
# Positive ref (+) unroll the cable --> Moves the car down
# Negative ref (-) roll up --> Moves the car up

distance = 0 # Distance to move the anres
angleRef = 0 # Angle reference to move the arnes with a position control, we only use it in Distance mode

PULLEY_DIAMETER = 6.35 # Diameter of the pulley in cm
CIRCU_PULLEY = PULLEY_DIAMETER * pi # Circumfrence of the pulley in cm
up_flag = True # Flag to indicate if we can go up --- True: We can move up, False: we can't move up we can only move down
down_flag = True # Flag to indicate if we can go down

# Identify if we already up or down
if upper_sensor.value() == 1: # If the upper sensor is activated then we cannot go up
    up_flag = False 
elif lower_sensor.value() == 1:# If the lower sensor is activated then we cannot go down
    down_flag = False 
    
speed = 0 # Speed to move the pulley, we only use it for Velocity mode
mode = 'Distance' # Mode that we're working, there are two modes Distance and Velocity
def reciveMove():
    global angleRef, distance, speed, mode
    while True:
        _, msg = esp.recv()
        if msg:
            if msg == b'Up' and up_flag: # Move the pulley to move up the car
                distance = -35
            elif msg == b'Down' and down_flag: # Move the pulley to move down the car
                distance = 34
            elif msg == b'Stop': # Stop the pulley
                mode = 'Distance'
                distance = 0
                angleRef = 0
            else:
                distance = 0
            nSpin = distance / CIRCU_PULLEY 
            angleRef = 360 * nSpin # Obtain the angle in degrees to move the pulley
            
            if msg == b'UpCar': 
                speed = -20
                mode = 'Velocity'

def sensor():
    global down_flag, up_flag
    while True:
        upState = upper_sensor.value()
        downState = lower_sensor.value()
        # Change the upper_flag
        if upState == 1:
            up_flag = False             
        else:
            up_flag = True
        # Change the lower_flag
        if downState == 1:
            down_flag = False
            esp.send(peer_esp5, 'Last') # When we are in the bottom, we send a feedback to the ESP32 5 to say that we are in the last cycle
        else:
            down_flag = True        
        time.sleep_ms(15)
        
_thread.start_new_thread(reciveMove, ())
_thread.start_new_thread(sensor, [])
# ==================== MAIN ==================================================
if __name__ == '__main__':
    # PIN SETUP
    pinMAR = PinMotorArnes(23,22,21,19)
    # ================ CREATING MOTOR OBJETS =======================================
    motorArnes = Arnes(pinMAR, 3.197, 26.3267, 0.097059, (145.6 * 28), 14,0.25,0)
    b_enviado = False # Flag to indicate to finally stop the rutine
    while(True):
        if mode == 'Distance':
            pos_MAR = 4.25*(position_MAR* 360.0 /motorArnes.ppr) # Calculo de angulo
            
            distance_ob = pos_MAR * CIRCU_PULLEY/360 # Distance obtain, we use it to compare with the reference
            sub = abs(distance - distance_ob)    # This is a tolerence to stop the control position
            
            if distance > 0 and down_flag and sub > 0.5: # Move the car down
                motorArnes.moveMotorPos(angleRef, pos_MAR, Tm)
                up_flag = True   
            elif distance < 0 and up_flag and sub > 0.5: # Move the car up
                motorArnes.moveMotorPos(angleRef, pos_MAR, Tm)
                down_flag = True
            elif sub <= 0.5 or up_flag == False or down_flag == False: # Stop moving the pulley
                motorArnes.stopMotor()
                msg="Detener"
                esp.send(peer_esp1,msg) # Send a message to ESP32 1 to stop moving the car
                position_MAR = 0
                pos_MAR = 0
                distance = 0   
        elif mode == 'Velocity':
            velMAR = motorArnes.obtainVelocity(Tm)
            if up_flag ==  True:
                motorArnes.moveMotorVel(speed, velMAR, Tm)
            else:
                motorArnes.stopMotor()
                if b_enviado == False:
                    esp.send(peer_esp1, 'Stop') # Send a message to ESP32 1 to stop the rutine
                    b_enviado = True
        time.sleep_ms(50)        
    