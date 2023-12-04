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

    esc = chr(27)
    stx = chr(2)
    ext = chr(3)
    eot = chr(4)

    # ESC file to set embossing head 2 direction printing
    # CHD-1,EX320;

    # line spacing
    # LS0;

    # s.write("LS0;".encode())
    s.write(stx.encode())
    s.write("\n\n\n".encode())
    # s.write("AAAAAAAAA\n".encode())
    # s.write("BBBBBBBBB\n".encode())
    # s.write("CCCCCCCCCC\n".encode())
    # s.write("DDDDDDDDDDD\n".encode())
    # s.write("EEEEEEEEEEEE\n".encode())
    for i in range(3):  # 34
        text = "=" * 48
        print(f"sending {text}")
        s.write(f"{text}\n".encode())
        # s.write("LD20;".encode())

    s.write(ext.encode())
    s.write(eot.encode())

    # \x1b = ESC

    # temporary page length to 500mm
    # <1B><44><PL><500>
    # s.write(b'\x1b\x44')
    # s.write("PL500".encode())

    # s.write(b'\x1b\x44')
    # s.write("BPTEST1234".encode())

    # s.write(b'\x1b\x44')
    # s.write(f"{esc}DBPTEST1234".encode())

    # s.write(eot.encode())

    ret = s.read(2)
    print(len(ret))
    print(ret)
    ret = ret.decode()
    print(ret)
