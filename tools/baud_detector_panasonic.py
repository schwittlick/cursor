import serial
import sys
import chardet
import struct

if __name__ == "__main__":
    bauds = [
        #    75,
        #    110,
        #    150,
        # 200,
        300,
        # 600,
        # 1200,
        # 2400,
        # 4800,
        # 9600,
        # 19200,
        # 38400,
        # 57600,
        # 74880,
        # 115200,
    ]
    port = "COM3"
    response = ""
    letters = [
        chr(27) + "j" + "n",
        chr(27) + "@",
        chr(27) + "c" + "\n\r",
        chr(11) + "\n\r",
        chr(0) + "\n\r",
        chr(13) + "\n\r",
        #  "H\n\r",
        #  "CAN",
        #  "DC1",
        #  "BS",
        #  "CR;",
        #  "X",
        #  "FF",
        #  "I",
        #  "I\n\r",
        #  "I;",
        #  "I;\n\r",
        #  "H;",
        #  "D",
        #  "J100,0",
        #  "M0,-50",
        #  "I: D100,100,100,150,150,10",
        #  "Y100",
        # "POF",
        # "IMS:1",
        # "IMS:123",
        # "AVL:123",
    ]
    for baud in bauds:
        print(baud)
        s = serial.Serial(
            port,
            baud,
            timeout=0.3,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
        )
        for letter in letters:
            # s.write(b"SP1;")
            s.write(b"{letter}")
            response = s.readline()

            # print(letter)
            if response:
                if response != b"\\\x9c\x9c\\\\\x9c\x9c|\xfb":
                    print("im special")
                a, txt = struct.unpack("I5s", response)
                print(txt.decode("windows-1252"))

                print(response)
                enc = chardet.detect(response)["encoding"]
                print(f"enc: {enc}")
                r2 = response.hex()
                bytes_object = bytes.fromhex(r2)
                ascii_string = bytes_object.decode("latin-1")
                print(f"decoded: {ascii_string}")
                print("------")

                response = ""
        print(response)
        s.close()
        if response:
            print(f"{baud} - {response}")
            string = response.decode("utf-8")
            print(string)
            # print(response.hex().decode("hex"))
            sys.exit(0)
