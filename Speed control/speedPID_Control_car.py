import machine
import time
from PinMotor import PinMotor

class Motor: 
    direction = 1    
    def __init__(self, pinMotor, Kp_Vel = 1, Ki_Vel = 0, Kd_Vel = 0, ppr = 1,
                 Kp_Pos = 1, Ki_Pos = 0, Kd_Pos = 0):
        self.motor = pinMotor # Object that contains the pins
        self.in1 = self.motor.enA_Motor # Pin that contains the OUT 1 of the driver
        self.in2 = self.motor.enB_Motor # Pin that contains the OUT 2 of the driver
        self.pinPWM = self.motor.pin_PWM # Pin that contains the PWM
        # Gains for PID velocity control
        self.Kp_Vel = Kp_Vel
        self.Ki_Vel = Ki_Vel
        self.Kd_Vel = Kd_Vel
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
        pwm = int(self.controlMotorVel(setpoint, velocity,Tm)) # Calls the velocity control
        if(pwm<0): # Check the direction of the wheel
            Motor.direction = -1
        else: 
            Motor.direction = 1
        # PWM's saturation, the maximum is 95% of the width
        pwm = abs(pwm)
        if(pwm>970):
            pwm = 970
        # Moves the motor
        self.pinPWM.freq(1000)
        self.pinPWM.duty(pwm)
        if(Motor.direction == 1):
            self.in1.value(1)
            self.in2.value(0)
        elif(Motor.direction == -1):
            self.in1.value(0)
            self.in2.value(1)
            
    # This method moves the motor at a certain position in degrees
    def moveMotorPos(self, setpoint, position,Tm):
        pwm = int(self.controlMotorPos(setpoint, position,Tm)) # Calls the position control
        if(pwm<0): # Check the direction of the wheel
            Motor.direction = -1
        else: 
            Motor.direction = 1
        # PWM's saturation, the maximum is 95% of the width
        pwm = abs(pwm)
        if(pwm>970):
            pwm = 970
        # Moves the motor
        self.pinPWM.freq(1000)
        self.pinPWM.duty(pwm)
        if(Motor.direction == 1):
            self.in1.value(1)
            self.in2.value(0)
        elif(Motor.direction == -1):
            self.in1.value(0)
            self.in2.value(1)
            
    # This method contains the velocity control
    def controlMotorVel(self,setpoint,velocity,Tm):
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

# ===============================================================================================================
# ===============================================================================================================
# ===============================================================================================================

Tm = 0.05 # Sampling time in seconds

# ==================== MAIN ==================================================
if __name__ == '__main__':
    # PIN SETUP
    pinMC1 = PinMotor(13,14,27,39,34)   # Pins for the car's motor 1
    pinMC2 = PinMotor(26,25,33,32,35)   # Pins for the car's motor 2
    # ================ CREATING MOTOR OBJETS =======================================
    motorMC1 = Motor(pinMC1, 3.4833, 18.4698, 0.16424, 3892, 5.75, 0.008, 0)
    motorMC2 = Motor(pinMC2, 3.5865,19.573, 0.1643, 3892,5.75, 0.008,0)

    while(True):
        # ---------------- Velocity for MC1 ------------------
        velMC1 = motorMC1.obtainVelocity(Tm) 
        # ---------------- Velocity for MC2 ------------------
        velMC2 = motorMC2.obtainVelocity(Tm)
        # ========= MOVIMIENTO DEL MOTOR ======================
        
        # Moving the car in a Open Loop
        # motorMC2.moveMotorOL(255,frequency) 
        
        # Moving the car in a Close Loop
        # Positive value: moves the car down
        # Negative value: moves the car up
        car_speed = -20 
        motorMC2.moveMotorVel(car_speed,velMC2,Tm) 
        motorMC1.moveMotorVel(-1*car_speed,velMC1,Tm) 
        
        print(f'Ref: {car_speed} -- MC1: {velMC1} -- MC2: {velMC2}')
        time.sleep_ms(50)        