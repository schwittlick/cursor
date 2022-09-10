import serial
import sys
import codecs
import time

if __name__ == "__main__":
    bauds = [
        #  75,
        #  110,
        #  150,
        #  200,
        #  300,
        #  600,
        #  1200,
        #    2400,
        #  4800,
        9600,
        #  19200,
        #  38400,
        #  57600,
        #  74880,
        #  115200,
    ]
    port = "COM3"
    response = ""
    for baud in bauds:
        s = serial.Serial(
            port,
            baud,
            timeout=1,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
        )
        s.write(b"OH;")
        response = s.readline()
        print(response)
        s.write(b"IN;SP1;PU100,100;")
        time.sleep(1)
        response2 = s.readline()
        print(f"response2: {response2}")
        s.close()
        if response:
            print(f"{response}")
            # string = response.decode('hex')
            string = response[1:]
            # r1 = string[:1] + string[2:]
            r2 = string.hex()
            print(string)
            print(r2)
            bytes_object = bytes.fromhex(r2)
            ascii_string = bytes_object.decode("latin-1")
            print(ascii_string)
            # string.remove(4)
            print(string)
            s = codecs.decode(r2, "hex")
            print(s)
            # string = bytearray.fromhex(string.decode('utf-8')).decode()
            # print(string)
            # print(response.hex().decode("hex"))
            sys.exit(0)
