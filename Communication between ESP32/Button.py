import machine
import utime


class Button:
    mode = 'Manual'
    def __init__(self, pin, esp, msg_True, msg_False = "", peer=b""):
        # Attributes 
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN) # pin: Contains the pin of the button
        self.msg_True = msg_True # msg_True: this is the msg it sends when you push the button and change the flag to true
        self.msg_False = msg_False # msg_False: this is the msg it sends when you push the button and change the flag to false
        self.esp = esp # This is the esp we are working on
        self.peer = peer 
        
        self.last_state = 0 # Last state of the button, this is for the debounce function
        self.debounce = 10 # Debounce of the button in MILISECONDS
        self.flag_state = False # This flag indicates which msg should the ESP32 send, the msg os acording to the msg_True and msg_False
    
    # This method contains an algorithm for the debounce of the button
    def reading(self): 
        current_state = self.pin.value() # Read the first state of the button
        # Check if there's a change between the current state and the last state
        if current_state != self.last_state: 
            # Leave some time to aviod the bounces of the mecanic button
            utime.sleep_ms(self.debounce) 
            # Re read the state of the button
            current_state = self.pin.value() 
            # Re-check the two states, if they're different then is a correct change
            if current_state != self.last_state and current_state ==  1: 
                if current_state == 1: # Sees if the state of the button is 1
                    self.flag_state = not self.flag_state # Change the flag
                    
                if self.flag_state == True and Button.mode == 'Manual': # Se in what mode are we
                    msg = self.msg_True
                    self.esp.send(self.peer, msg)
                    print(msg)
                    if self.msg_True == 'Auto':
                        Button.mode = 'Auto'
                    

                elif self.flag_state == False and Button.mode == 'Manual':
                    msg = self.msg_False
                    self.esp.send(self.peer, msg)
                    print(msg)
                    
                # If the mode is Auto then we stop reading the sate of the buttons, give the control to ESP32 5 and only have access to the button Stop
                elif Button.mode == 'Auto' and self.flag_state == True:
                    Button.mode = 'Manual'
                    print(Button.mode)
                    msg = self.msg_False
                    self.esp.send(self.peer, msg)
            self.last_state = current_state # Change the last state, this for a next change in the button
