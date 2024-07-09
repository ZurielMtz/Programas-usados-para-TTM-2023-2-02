import machine
import time
from PinMotor import PinMotor
# You must run first this program 
# This program has be uploaded to the ESP32 and connect to a UBS port using the pins 16 and 17

class Motor: 
    direction = 1    
    def __init__(self, pinMotor):
        self.motor = pinMotor # Object that contains the pins
        self.in1 = self.motor.enA_Motor # Pin that contains the OUT 1 of the driver
        self.in2 = self.motor.enB_Motor # Pin that contains the OUT 2 of the driver
        self.pinPWM = self.motor.pin_PWM # Pin that contains the PWM
        # Velocities for an ARMA filter
        self.vel_n1 = 0 # v[n-1]
        self.vel_n2 = 0 # v[n-2]

    # This method moves the motor in a Open Loop, this does not contain a control
    def moveMotorOL(self,pwm,frequency):
        self.pinPWM.freq(frequency)
        self.pinPWM.duty(pwm)
        if(Motor.direction == 1):
            self.in1.value(1)
            self.in2.value(0)
        elif(Motor.direction == -1):
            self.in1.value(0)
            self.in2.value(1)
   
    # This methods stops the motor and put the errors to zero
    def stopMotor(self):
        self.pinPWM.duty(0)
        self.in1.value(0)
        self.in2.value(0)
        self.error_n1 = 0
        self.error_n2 = 0
        self.u_n1 = 0
        self.vel_n1 = 0
        self.vel_n2 = 0
        
    # This method give us the velocity of the wheel using an ARMA filter
    def obtainVelocity(self, Tm):
        vel_n0 = 4.25*((self.motor.positionMotor - self.motor.prevPositionMotor)/Tm)*(60.0/self.ppr) # Obatin the velocity
        self.motor.prevPositionMotor = self.motor.positionMotor # Update the previous position
        velocity = (vel_n0 + self.vel_n1 + self.vel_n2)/3 # ARMA Filter
        # Updates previous velocities
        self.vel_n2 = self.vel_n1
        self.vel_n1 = vel_n0
        return velocity
    
# Initialize the UART communication
uart = machine.UART(2,115200)

Tm = 0.05 # Sampling time in SECONDS

stop = False
def stop(): # This function reads the port if we need to stop the program
    global stop
    if uart.any():
        data = uart.readline().decode('utf-8')
        stop = bool(data)
        
# ==================== MAIN ==================================================
if __name__ == '__main__':
    frequency = 1000
    pin_Motor = PinMotor(13, 14, 27, 39, 34) # Pins for the motor
    motor = Motor(pin_Motor)
    
    tension = float(input('Insert the tension of the motor: '))
    if tension > 11.3:
        tension = 11.3
    elif tension < -11.3:
        tension = -11.3
    
    pwm = int(tension * 970 / 11.3)
    
    while not stop: # This while loop will run until it recives a stop from the serial communiction
        str_vel = str(velMotor) + '\n'
        uart.write(str_vel.encode())
        # ---------------- Velocity for the Motor ----------------
        velMotor = motor.obtainVelocity(Tm)
        
        # Moves the motor in an Open Loop
        motor.moveMotorOL(pwm,frequency)
        # motorArnes.moveMotorOL(pwm,frequency)
        print(f'Speed: {velMotor}')
        time.sleep_ms(50)
        stop()
        
    motor.stopMotor()
    