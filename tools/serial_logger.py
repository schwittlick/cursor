import serial
import time
import sys


if __name__ == "__main__":
    s = serial.Serial(
        port="/dev/ttyUSB1", baudrate=300, parity=serial.PARITY_NONE, timeout=2
    )
    b = b""
    logs = {}
    c = 0
    while True:
        b = s.read(2)
        st = b.decode("utf-8", errors="replace")
        if st == "\n" or b == b"\n":
            print("LINEBREAK")
        print(st)
        ts = time.time()
        if b in logs:
            logs[b] += 1
        else:
            logs[b] = 0
        # logs.append((b, ts))
        if c % 100 == 0:
            pass
            # so = {k: v for k, v in sorted(logs.items(), key=lambda item: item[1], reverse=True)}
            # print(so)
        c = c + 1
        # print(b)
        continue
        if b == b"\x00":
            sys.stdout.write(" ")
            sys.stdout.flush()
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
