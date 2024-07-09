import serial
from openpyxl import Workbook
import time

# This program needs to run in a computer and be conected to a ESP32 by USB
# and stores the information in an Excel file

# Creates an Excel file, ***** as a note the file must not exist before runing the code
file_name = 'MR5.xlsx' # Name of the Excel file
book = Workbook()
sheet = book.active
sheet.title = 'V6' # Name of the sheet

# Columns of the sheet
sheet['A1'] = 'Time [ms]'
sheet['B1'] = 'Speed [RPM]'
sheet['C1'] = 'Tension [V]'

if __name__ == '__main__':
    port = serial.Serial('COM12',115200) # Comunicates to the port
    time.sleep(1)
    
    initial_time = time.time() # Obtain the time in seconds
    final_time = time.time()
    
    list = []
    timee = 0 
    while (final_time - initial_time) <= 60: # This while loop will loop for 60 seconds
        final_time = time.time()
        # Waits for data in the port
        if port.in_waiting > 0:
            speed = port.readline()
            speed = float(speed.decode('ascii'))
            print(f'speed: {speed}')
            list.append([timee,speed, 5]) # The last value is tension
            timee += 0.05
        
    for data in list: # Stores the information in the sheet
        sheet.append(data) 
    
    # Save the workbook        
    book.save(file_name)
    stop = 'True'
    port.write(stop.encode()) # Send a msg to the port to stop moving the motor