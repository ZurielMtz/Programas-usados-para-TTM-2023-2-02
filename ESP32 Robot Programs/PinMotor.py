import machine

class PinMotor:
    def __init__(self, enA_Motor, enB_Motor, pin_PWM, encoderA, encoderB):
        # ================ PIN SETUP ========================================
        self._enA_Motor = machine.Pin(enA_Motor, machine.Pin.OUT) #Out 1 of the driver motor
        self._enB_Motor = machine.Pin(enB_Motor, machine.Pin.OUT) # Out 2 for the driver motor
        self._pin_PWM = machine.PWM(pin_PWM) # pin for the PWM of the driver
        self._encoderA = machine.Pin(encoderA, machine.Pin.IN) # Channel A of motor's encoder
        self._encoderB = machine.Pin(encoderB, machine.Pin.IN) # Channel B of motor's encoder
        
        self._positionMotor = 0 # Current position
        self._prevPositionMotor = 0 # Previous postion
        self._pin_PWM.init(freq = 1000, duty = 0) # Initialize the PWM
        self._encoderA.irq(trigger = machine.Pin.IRQ_RISING, handler = self.interruptMotor) # Defines a pin for interrupts
    
    # This method is for interruptions
    def interruptMotor(self):  # Every rising edge we enter to the interrupt
        if(self._encoderB.value() > 0): 
            self._positionMotor += 1 # CCW
        else:
            self._positionMotor -= 1 # CW
            
    # -------------------- SETTERS AND GETTERS ------------------------------------------------
    @property
    def enA_Motor(self):
        return self._enA_Motor
    @property
    def enB_Motor(self):
        return self._enB_Motor
    @property
    def pin_PWM(self):
        return self._pin_PWM
    
    @property
    def positionMotor(self):
        return self._positionMotor
    @positionMotor.setter
    def positionMotor(self, positionMotor):
        self._positionMotor = positionMotor
    
    @property
    def prevPositionMotor(self):
        return self._prevPositionMotor
    @prevPositionMotor.setter
    def prevPositionMotor(self, prevPositionMotor):
        self._prevPositionMotor = prevPositionMotor
    