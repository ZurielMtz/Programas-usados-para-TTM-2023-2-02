import machine
import time

enA_Actuator = machine.Pin(12, machine.Pin.OUT)
enB_Actuator = machine.Pin(15, machine.Pin.OUT)

SPEED_ACTU = 3.41 # mm/s # Constant Speed for a load of 3Kg

if __name__ == '__main__':
    
    # Negative distance ---> pull in the piston 
    # Positivedistance ----> pull out the piston
    distance = float(input("Insert the distance to move in mm [(-) Pull in, (+) Pull out]: "))
    timee = abs(distance / SPEED_ACTU)
    print(f'Time: {timee} s')
    if(distance>=0):
        enA_Actuator.value(1)
        enB_Actuator.value(0)
    else:
        enA_Actuator.value(0)
        enB_Actuator.value(1)
    time.sleep(timee)
    enA_Actuator.value(0)
    enB_Actuator.value(0)