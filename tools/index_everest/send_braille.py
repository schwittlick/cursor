import serial

if __name__ == "__main__":
    port = "/dev/ttyUSB4"
    baud = 9600
    response = ""
    s = serial.Serial(
        port,
        baud,
        timeout=1,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=True
    )
    print(s.is_open)

    file = "data/test_width.vim"

    with open(file, "r") as vim:
        lines = vim.readlines()
        for line in lines:
            s.write(line.encode())
