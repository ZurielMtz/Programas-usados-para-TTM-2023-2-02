import machine
import time
from math import pi
from PinMotorArnes import PinMotorArnes

class Arnes:
    direction = 1 
    def __init__(self,pinMotor, Kp = 1, Ki = 0, Kd = 0, ppr = 1,
                 Kp_Pos = 1, Ki_Pos = 0, Kd_Pos = 0):
        self.motor = pinMotor # Object that contains the pins
        self.pinPWM1 = self.motor.pin_PWML # Pin that contains the PWM 1 of the driver
        self.pinPWM2 = self.motor.pin_PWMR # Pin that contains the PWM 2 of the driver
        # Gains for PID velocity control
        self.Kp = Kp 
        self.Ki = Ki
        self.Kd = Kd
        self.ppr = ppr # Pulse per revolution --> Gear reduction * Encoder quadrature
        # Gans for PID position control
        self.Kp_Pos = Kp_Pos
        self.Ki_Pos = Ki_Pos
        self.Kd_Pos = Kd_Pos
        # Errors of the control
        self.error_n1 = 0 # e[n-1]
        self.error_n2 = 0 # e[n-2]
        self.u_n1 = 0 # u[n-1]
        # Velocities for an ARMA filter
        self.vel_n1 = 0 # v[n-1]
        self.vel_n2 = 0 # v[n-2]

    # This methos moves the motor at a certain speed in a Close Loop
    def moveMotorVel(self, setpoint, velocity,Tm):
        pwm = int(self.controlMotor(setpoint, velocity,Tm)) # Calls the velocity control
        if(pwm<0): # Check the direction of the arnes
            Arnes.direction = -1
        else: 
            Arnes.direction = 1
        # PWM's saturation, the maximum is 95% of the width
        pwm = abs(pwm)
        if(pwm>970):
            pwm = 970
        # Moves the motor
        self.pinPWM1.freq(1000)
        self.pinPWM2.freq(1000)
        if(Arnes.direction == 1):
            self.pinPWM1.duty(pwm)
            self.pinPWM2.duty(0)
        elif(Arnes.direction == -1):
            self.pinPWM1.duty(0)
            self.pinPWM2.duty(pwm)
            
    # This method moves the motor at a certain position in degrees
    def moveMotorPos(self, setpoint, position,Tm):
        pwm = int(self.controlMotorPos(setpoint, position,Tm)) # Calls the position control
        if(pwm<0): # Check the direction of the arnes
            Arnes.direction = -1
        else: 
            Arnes.direction = 1
        # PWM's saturation, the maximum is 95% of the width
        pwm = abs(pwm)
        if(pwm>970):
            pwm = 970
        # Moves the motor
        self.pinPWM1.freq(1000)
        self.pinPWM2.freq(1000)
        if(Arnes.direction == 1):
            self.pinPWM1.duty(pwm)
            self.pinPWM2.duty(0)
        elif(Arnes.direction == -1):
            self.pinPWM1.duty(0)
            self.pinPWM2.duty(pwm)
    
    # This method contains the velocity control
    def controlMotor(self,setpoint,velocity,Tm):
        error = setpoint - velocity # Obtain the error
        p = self.Kp_Vel * (error - self.error_n1)  # Proporcional value
        i = + (self.Ki_Vel*Tm/2) * (error + self.error_n1) # Integral value
        d = (self.Kd_Vel/Tm) * (error - 2*self.error_n1 + self.error_n2)  # Derivative value
        u = p + i + d + self.u_n1 #u[n]
        
        # Updates the previous errors
        self.error_n2 = self.error_n1
        self.error_n1 = error
        self.u_n1 = u
        return u 
    
        # This method contains the position control
    def controlMotorPos(self,setpoint,position,Tm):
        error = setpoint - position # Obtian the error
        p = self.Kp_Pos * (error - self.error_n1)  # Proporcional value
        i = + (self.Ki_Pos*Tm/2) * (error + self.error_n1) # Integral value
        d = (self.Kd_Pos/Tm) * (error - 2*self.error_n1 + self.error_n2)  # Derivative value
        u = p + i + d + self.u_n1 # u[n]
        
        # Updates the previous errors
        self.error_n2 = self.error_n1
        self.error_n1 = error
        self.u_n1 = u
        return u 

    # This method moves the motor in a Open Loop, this does not contain a control
    def moveMotorOL(self,pwm,frequency):
        self.pinPWM1.freq(frequency)
        self.pinPWM2.freq(frequency)
        if(Arnes.direction == 1):
            self.pinPWM1.duty(pwm)
            self.pinPWM2.duty(0)
        elif(Arnes.direction == -1):
            self.pinPWM1.duty(0)
            self.pinPWM2.duty(pwm)
    
    # This methods stops the motor and put the errors to zero
    def stopMotor(self):
        self.pinPWM1.duty(0)
        self.pinPWM2.duty(0)
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
# ===============================================================================================================
# ===============================================================================================================


Tm = 0.05 # Sampling time in SECONDS

PULLEY_DIAMETER = 6.35 # Diameter of the pulley in cm
CIRCU_PULLEY = PULLEY_DIAMETER * pi # Circumfrence of the pulley in cm

# ==================== MAIN ==================================================
if __name__ == '__main__':
    
    pinMAR = PinMotorArnes(23,22,21,19)
    # ================ CREATING MOTOR OBJETS =======================================
    motorArnes = Arnes(pinMAR, 3.197, 26.3267, 0.097059, (145.6 * 28), 14,0.25,0)
        
    distance = float(input('Insert the distance to move in cm [(-) roll up the cable,  (+) unroll the cable]: '))
    # Obtain the angle in degrees to move
    nSpin = distance / CIRCU_PULLEY
    angleRef = 360 * nSpin
    while(True):
        # ========= MOVING THE MOTOR ======================
        pos_MAR = 4.25*(pinMAR.positionMotor* 360.0 /motorArnes.ppr) # Calculates the angle in degrees
        
        distance_ob = pos_MAR * CIRCU_PULLEY/360 # Distance obtain, we use it to compare with the reference
        
        # Moves the arnes at a postion with a Close Loop
        motorArnes.moveMotorPos(angleRef, pos_MAR, Tm)
        
        distance_ob = pos_MAR * CIRCU_PULLEY/360
        print(f'Ref: {angleRef}  --- Distance Arnes {distance_ob}')
        time.sleep_ms(50)        
    
    




