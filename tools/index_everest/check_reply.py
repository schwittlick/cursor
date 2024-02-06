import serial

if __name__ == "__main__":
    port = "/dev/ttyUSB4"
    baud = 9600
    response = ""
    s = serial.Serial(
        port,
        baud,
        timeout=8,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=True
    )
    print(s.is_open)

    esc = chr(27)
    stx = chr(2)
    ext = chr(3)
    eot = chr(4)

    s.write(f"1===============================================================".encode())
    ret = s.readline()
    print(ret)