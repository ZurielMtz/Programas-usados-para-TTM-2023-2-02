import machine
import utime

class LimitSensor:
    flag_state = False
    def __init__(self, pin, msg_True, esp, msg_False = "", msg_next = '', msg_stay = '',peer=b""):
        # Attributes
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN)  # Pins that contains the horizontal limit switch
        self.msg_True = msg_True #msg_True: this is the msg it sends when you push the button and change the flag to true
        self.msg_False = msg_False # msg_False: this is the msg it sends when you push the button and change the flag to false
        self.esp = esp # This is the esp we are working on
        self.msg_next = msg_next # This indicates the next state for the Auto mode, it send it to the ESP32 2 
        self.msg_stay = msg_stay # This is used to stay in the current state of th Auto mode
        self.peer = peer
        
        self.last_state = 0 # Contains the last state of the limit switch
        self.bounce = 10 # Time of debounce function in MILISENCODS
        
     
    # This method contains an algorithm for the debounce of the limit switch when we are working in Manual mode   
    def readManual(self):
        current_state = self.pin.value() # Read the first state of the button
        # Check if there's a change between the current state and the last state
        if current_state != self.last_state: 
            # Leave some time to aviod the bounces of the mecanic button
            utime.sleep_ms(self.debounce) 
            # Re read the state of the button
            current_state = self.pin.value() 
            # Re-check the two states, if they're different then is a correct change
            if current_state != self.last_state and current_state ==  1: 
                if current_state == 1: # When the limit switch is press then stop then send a msg to stop the rails
                    message = self.msg_True
                    self.esp.send(self.peer, message)
                else:
                    message = self.msg_False
                    self.esp.send(self.peer, message)
    
    # This method contains an algorithm for the debounce of the limit switch when we are working in Auto mode 
    def readAuto(self):
        current_state = self.pin.value()
    
        if current_state != self.last_state:            
            utime.sleep_ms(self.bounce)
            current_state = self.pin.value()
            if current_state != self.last_state:
                if current_state == 1: # Send a msg to stop the rails
                    LimitSensor.flag_state = False # Change the state of the flag that has send it already
                    message = self.msg_True
                    self.esp.send(self.peer, message)
                    return self.msg_next # Return the next state
                else: # This happens when the limit switch is nos pressed
                    message = self.msg_False
                    self.esp.send(self.peer, message)
                    return self.msg_stay # Return the current state 