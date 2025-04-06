import serial
import time

def format_hex(byte_data):
    return ' '.join(f'{b:02X}' for b in byte_data)

def register_rfid(rfid_data, stored_data):
    # Ask user if they want to register this new RFID
    response = input(f"\nDo you want to register this new RFID: {rfid_data}?\nYes or No: \n:: ").strip().lower()
    if response == "yes":
        stored_data.append(rfid_data)
        print(f"RFID {rfid_data} registered.\n")
        return True
    else:
        print("RFID registration canceled.\n")
        return False


# Initialize the stored RFID data list (You can also load this from a file or database)
stored_rfid_data = []

# Store the last scanned RFID to prevent multiple registrations
last_scanned_rfid = None

arduino_com = 'COM20'
rfid_com = 'COM15'

try:
    rfid_port = serial.Serial(rfid_com, 57600, timeout=1)
    arduino_port = serial.Serial(arduino_com, 9600, timeout=1)
    print("Connected to RFID Reader and Arduino.")
except serial.SerialException as e:
    print("Error:", e)
    exit()

time.sleep(2)

while True:
    try:
        # --- Read from RFID reader ---
        if rfid_port.in_waiting:
            raw_data = rfid_port.read(rfid_port.in_waiting)
            if raw_data:
                hex_data = format_hex(raw_data)
                rfid_data = hex_data[:59]

                print("RFID DATA HEX:", rfid_data)

                # Check if this RFID data is the same as the last scanned data
                if rfid_data != last_scanned_rfid:
                    last_scanned_rfid = rfid_data  # Update the last scanned RFID

                    # Check if this RFID data is already registered
                    if rfid_data not in stored_rfid_data:
                        print("This RFID is not registered.")
                        # Prompt user to register if not already registered
                        if register_rfid(rfid_data, stored_rfid_data):
                            # Send the RFID data to Arduino after registration
                            arduino_port.write((rfid_data + '\n').encode())
                    else:
                        print("RFID is already registered.")
                        # Send the RFID data to Arduino if registered
                        arduino_port.write((rfid_data + '\n').encode())
                else:
                    print("RFID already processed. Skipping...\n")

        # --- Read from Arduino ---
        if arduino_port.in_waiting:
            arduino_data = arduino_port.readline().decode().strip()
            if arduino_data:
                print("Arduino says:")
                print(arduino_data)
                print("-" * 100)

    except Exception as e:
        print("Error:", e)
