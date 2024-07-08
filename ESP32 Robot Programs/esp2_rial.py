import network
import espnow
import machine
import _thread
import time
from Motor import Motor
from PinMotor import PinMotor

Tm = 0.05 # Sampling time in SECONDS****

# =========== CONECTION FOR ESP32 2 ===========================================
sta = network.WLAN(network.STA_IF) 
sta.active(True)
# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

# ============== THREADS ======================================================
# ========= ROBOT MOVEMENT ======================
# To move the robot  positive reference (+): right 
#                    negative reference (-): left

speed_ref = 0 # Speed reference for the upper wheels
speed_ref2 = 0 # Speed reference fot the lower wheels
right_flag = True # Flag that indicates if we can move to the right -- True: Yes we can move, False: No we can't move
left_flag = True # Flag that indicates if we can move to the left

def reciveMove():
    global speed_ref, speed_ref2, right_flag, left_flag
    while True:
        _, msg = esp.recv() # This give us the host and the message 
        if msg:
            if msg == b'Right' and right_flag: # We move to the right
                speed_ref = 40 
                speed_ref2 = 30
                left_flag = True
            elif msg == b'Left' and left_flag: # We move to the left
                speed_ref = -40 
                speed_ref2 = -35
                right_flag = True
            elif msg == b'Stop' or left_flag == False or right_flag == False: # We stop the robot
                speed_ref = 0 
                speed_ref2 = 0
            # This if is for the limit sensors, the messages are from the ESP32 5
            if msg == b'Free': # We can move left or right
                left_flag = True
                right_flag = True
            elif msg == b'StopR': # We stop the robot on the right side of the solar panles
                speed_ref = 0 
                speed_ref2 = 0
                right_flag = False # We indicate that we can't move to the right so we can only move to the left
                left_flag = True
            elif msg == b'StopL': # We stop the robot on the left side of the robot
                speed_ref = 0 
                speed_ref2 = 0
                left_flag = False # We indicate that we can't move to the left so we can only move to the right
                right_flag = True
            
_thread.start_new_thread(reciveMove, []) # Thread that recives messages from the remote control or from ESP32 5
# This thread indicates how to move the robot horizontally 

if __name__ == '__main__':
    
    # PIN SETUP
    pinMR1 = PinMotor(5, 17, 16, 4, 2)    # Pins for the rail's motor 1
    pinMR2 = PinMotor(26, 25, 33, 32, 35) # Pins for the rail's motor 2
    pinMR3 = PinMotor(13, 14, 27, 39, 34) # Pins for the rail's motor 3
    pinMR4 = PinMotor(23, 22, 21, 19, 36) # Pins for the rail's motor 4
    
    # ================ CREATING MOTOR OBJETS =======================================
    motorMR1 = Motor(pinMR1, 2.8694, 11.0729, 0.078898, 1425.1)
    motorMR2 = Motor(pinMR2, 2.2579, 13.135, 0.09703, 1425.1)
    motorMR3 = Motor(pinMR3, 2.8853, 12.1378, 0.11719, 1425.1)
    motorMR4 = Motor(pinMR4, 3.2833, 13.3327, 0.11564, 1425.1)
    while(True):
        # ---------------- Velocity for MR1 ------------------
        velMR1 = motorMR1.obtainVelocity(Tm) # Obtain the velocity
        # ---------------- Velocity for MR2 ------------------
        velMR2 = motorMR2.obtainVelocity(Tm)
        # ---------------- Velocity for MR3 ------------------
        velMR3 = motorMR3.obtainVelocity(Tm)
        # ---------------- Velocity for MR4 ------------------
        velMR4 = motorMR4.obtainVelocity(Tm)       
    
        if(speed_ref < 0): # Case for moving to the left
            motorMR2.moveMotorVel(speed_ref2,velMR2,Tm) 
            motorMR4.moveMotorVel(-1*speed_ref,velMR4,Tm)
            motorMR1.moveMotorVel(speed_ref2,velMR1,Tm) 
            motorMR3.moveMotorVel(-1*speed_ref,velMR3,Tm)
        elif(speed_ref >0): # Cae for moving to the right
            motorMR1.moveMotorVel(speed_ref2,velMR1,Tm) 
            motorMR3.moveMotorVel(-1*speed_ref,velMR3,Tm)
            motorMR2.moveMotorVel(speed_ref2,velMR2,Tm)
            motorMR4.moveMotorVel(-1*speed_ref,velMR4,Tm)
        else: # Case for stoping the robot
            motorMR1.stopMotor()
            motorMR2.stopMotor()
            motorMR3.stopMotor()
            motorMR4.stopMotor()
        # Prints the references and the velocity of the motors            
        print(f'Ref1: {speed_ref2} -- M1: {velMR1} -- MR2: {velMR2} --Ref2: {speed_ref*-1} --- M3: {velMR3} -- M4: {velMR4}')
        time.sleep_ms(50)        
