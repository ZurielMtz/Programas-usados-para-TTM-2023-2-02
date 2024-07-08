import machine
import time
import _thread
import espnow
import network
from math import pi
from PinMotor import PinMotor
from Motor import Motor

# Pin setup for the actuator
enA_Actuator = machine.Pin(12, machine.Pin.OUT)
enB_Actuator = machine.Pin(15, machine.Pin.OUT)
enA_Actuator.value(0) # Set to 0 the pins for the actuator
enB_Actuator.value(0)
SPEED_ACTU = 3.41 # mm/s # Constant Speed for a load of 3Kg


Tm = 0.05 # Sampling time in SECONDS **** 

# =========== CONECTION FOR THE ESP32 1 ===========================================
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

# ==================== THREADS ======================================================
brush_speed = 0 # Speed reference for the brush
angleRef = 0 # Angle reference for the car's wheel, only use in Distance mode
mode = 'Distance' # Mode that we're working, there are two modes Distance and Velocity
car_speed = 0 # Speed reference for the car, only use in Velocity mode
WHEEL_DIAMETER = 6.2 # Diameter of the wheel
WHEEL_CIRCU = WHEEL_DIAMETER * pi # Circumference of the wheel in cm

def reciveMove():
    global brush_speed, angleRef, mode, car_speed
    while True:
        _, msg = esp.recv()
        if msg:
            if msg == b'Activate': # Activates the brush
                brush_speed = -180 
            elif msg == b'Desactivate': # Desactivates the brush
                brush_speed = 0  
            elif msg == b'Down': # Move the car 35cm down
                distance = 35
                nSpin = distance / WHEEL_CIRCU
                angleRef = 360 * nSpin # Obtain the angle in degrees to move the wheel
            elif msg == b'Up': # Move the car 35cm up
                distance = -35
                nSpin = distance / WHEEL_CIRCU
                angleRef = 360 * nSpin
            elif msg == b'Stop': # Stop the car
                angleRef = 0
                mode = 'Distance'
            elif msg == b'DownSys' or msg == b'UpSys': # Case if we need to move up or down the cleaning system
                distanceAct = 2 # Distance to move de actuator in mm
                timme = abs(distanceAct / SPEED_ACTU) 
                if msg == b'DownSys': # Case to move down the cleaning system
                    enA_Actuator.value(0)
                    enB_Actuator.value(1)
                    time.sleep(timme)
                elif msg == b'UpSys': # Case to move up the cleaing system
                    enA_Actuator.value(1)
                    enB_Actuator.value(0)
                    time.sleep(timme)    
                enA_Actuator.value(0) # Stop moving the actuator
                enB_Actuator.value(0)    
            # Case if we change the mode to Velocity            
            if msg == b'UpCar':
                car_speed = -20   
                mode = 'Velocity'
_thread.start_new_thread(reciveMove, [])

# ==================== MAIN ==================================================
if __name__ == '__main__':
    # Adjustment for the actuator
    time.sleep(1)
    distanceAct = 2.8
    timme = abs(distanceAct / SPEED_ACTU)    
    enA_Actuator.value(1)
    enB_Actuator.value(0)
    time.sleep(timme)
    enA_Actuator.value(0)
    enB_Actuator.value(0)    
    
    # PIN SETUP
    pinMC1 = PinMotor(13,14,27,39,34)   # Pins for the car's motor 1
    pinMC2 = PinMotor(26,25,33,32,35)   # Pins for the car's motor 2
    pinCEP1 = PinMotor(23,22,21,19,36)  # Pins for the brush motor 1
    pinCEP2 = PinMotor(5,17,16,4,2)     # Pins for the brush motor 2
    # ================ CREATING MOTOR OBJETS =======================================
    motorMC1 = Motor(pinMC1, 3.4833, 18.4698, 0.16424, 3892, 5.75, 0.008, 0)
    motorMC2 = Motor(pinMC2, 3.5865,19.573, 0.1643, 3892,5.75, 0.008,0)
    motorMCEP1 = Motor(pinCEP1, 0.17007, 0.78468, 0.0092148, 537.6, 1,0,0)
    motorMCEP2 = Motor(pinCEP2, 0.29756, 2.7376, 0.0080856, 537.6,1,0,0)

    while(True):
        if mode == 'Distance':
            posMC1 = 4.25*(pinMC1.positionMotor* 360.0 /motorMC1.ppr) # Obtain the angle in degrees
            posMC2 = 4.25*(pinMC2.positionMotor* 360.0 /motorMC2.ppr)
            
            # ================ MOVING THE CAR======================
            distance_ob = posMC2 * WHEEL_CIRCU/360 # Distance obtain, we use to compare with the distance reference
            if angleRef == 0: # If the angle reference is 0 then we stop the car
                motorMC1.stopMotor()
                motorMC2.stopMotor()
                distance = 0
                pinMC1.positionMotor = 0
                pinMC2.positionMotor = 0
                posMC1 = 0
                posMC2 = 0
            else:
                motorMC1.moveMotorPos(-1*angleRef,posMC1,Tm) # Move the car with a position control
                motorMC2.moveMotorPos(angleRef, posMC2,Tm)

        elif mode == 'Velocity':
            # ---------------- Velocity for MC1 ------------------
            velMC1 = motorMC1.obtainVelocity(Tm) 
            # ---------------- Velocity for MC2 ------------------
            velMC2 = motorMC2.obtainVelocity(Tm)
            
            if angleRef != 0: # We use angle reference to stop completely the car in any of the two modes
                motorMC2.moveMotorVel(car_speed,velMC2,Tm) 
                motorMC1.moveMotorVel(-1*car_speed,velMC1,Tm) 
            else:
                motorMC1.stopMotor()
                motorMC2.stopMotor()
        
        # ---------------- Velocity for MBSH1 ------------------
        velMCEP1 = motorMCEP1.obtainVelocity(Tm)
        # ---------------- Velocity for MBSH2 ------------------
        velMCEP2 = motorMCEP2.obtainVelocity(Tm)      
               
        # ========= MOVING THE BRUSH TO CLEAN THE PANEL ======================
        # + derecha - izquierda
        if(brush_speed != 0):
            motorMCEP1.moveMotorVel(brush_speed,velMCEP1,Tm)
            motorMCEP2.moveMotorVel(-1*brush_speed,velMCEP2,Tm)
        else:
            motorMCEP1.stopMotor()
            motorMCEP2.stopMotor()
        
        time.sleep_ms(50)           
