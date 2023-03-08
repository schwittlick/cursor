import serial.tools.list_ports


def discover() -> list:
    ports = list(serial.tools.list_ports.comports())
    data = []
    for port in ports:
        # Try to open the port
        try:
            ser = serial.Serial(port.device, baudrate=9600, timeout=0.5)
        except serial.SerialException:
            # If the port is already open, skip to the next one
            continue

        ser.write("OI;\n".encode("utf-8"))
        ret = ser.readline().decode("utf-8")
        model = ret.strip()
        if len(model) > 0:
            data.append((port.device, model))
            print(f"{port.device} -> {model}")
        ser.close()
    return data


if __name__ == '__main__':
    discover()
