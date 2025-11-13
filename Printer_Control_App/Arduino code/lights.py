import serial
import time
import serial.tools.list_ports

def find_arduino_port():
    # List all available ports
    ports = list(serial.tools.list_ports.comports())
    
    # Print the available ports
    print("Available serial ports:")
    for port in ports:
        print(f"Port: {port.device}, Description: {port.description}")
    
    # Search for Arduino in the ports list
    for port in ports:
        if "Arduino" in port.description or "usbserial" in port.device or "usbmodem" in port.device:
            print(f"Arduino found on port {port.device}")
            return port.device
    
    raise Exception("Arduino not found. Please check the connection.")

def set_brightness(ser, level):
    if 0 <= level <= 255:
        # Send the brightness level as a string followed by a newline
        ser.write(f"{level}\n".encode())
        time.sleep(0.1)  # Give time for the Arduino to process the command
    else:
        print("Brightness level must be between 0 and 255.")

# Find the Arduino port
arduino_port = find_arduino_port()

# Open serial connection with the found port
ser = serial.Serial(arduino_port, 9600)

# Allow some time for the connection to establish
time.sleep(2)

current_brightness = None  # Initialize a variable to store the current brightness

try:
    while True:
        # Ask user for brightness level
        user_input = input(f"Current brightness is {current_brightness}. Enter new brightness level (0-255) or 'q' to quit: ")

        if user_input.lower() == 'q':
            print("Exiting...")
            break

        try:
            # Convert the input to an integer
            brightness = int(user_input)
            if brightness != current_brightness:
                set_brightness(ser, brightness)
                current_brightness = brightness  # Update the current brightness
        except ValueError:
            print("Please enter a valid number between 0 and 255.")
finally:
    # Always close the serial connection when done
    ser.close()
