import machine
class PinMotorArnes:
    def __init__(self, pin_PWML, pin_PWMR, encoderA, encoderB):
        # ================ PIN SETUP ========================================
        self._pin_PWML = machine.PWM(pin_PWML) # pin for the PWM, this conects fisrt half of the driver
        self._pin_PWMR = machine.PWM(pin_PWMR) # pin for the PWM, this conects second half of the driver
        self._encoderA = machine.Pin(encoderA, machine.Pin.IN) # Channel A of motor's encoder
        self._encoderB = machine.Pin(encoderB, machine.Pin.IN) # Channel B of motors encoder
        
        self._positionMotor = 0 # Current position
        self._prevPositionMotor = 0 # Previous position
        self._pin_PWML.init(freq = 1000, duty = 0) # Initialize the two PWMs
        self._pin_PWMR.init(freq = 1000, duty = 0)
        self._encoderA.irq(trigger = machine.Pin.IRQ_RISING, handler = self.interruptMotor) # Defines a pin for interrupts
    
    # This method contains the interrupt        
    def interruptMotor(self): # This interrupt enter when there is a rising edge
        if(self._encoderB.value() > 0):
            self._positionMotor += 1 # CCW
        else:
            self._positionMotor -= 1 # CW
