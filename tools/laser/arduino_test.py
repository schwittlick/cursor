import serial

if __name__ == '__main__':
    arduino = serial.Serial("/dev/ttyACM0")
    lines = arduino.readline()
    print(lines)
    arduino.write("100".encode())
    lines = arduino.readline()
    print(lines)
    arduino.close()