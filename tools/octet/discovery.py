import threading

import serial.tools.list_ports
import wasabi

logger = wasabi.Printer(pretty=True, no_print=False)

def async_discover(serial_port):
    try:
        ser = serial.Serial(serial_port, baudrate=9600, timeout=5)
        ser.write("OI;\n".encode("utf-8"))
        ret = ser.readline().decode("utf-8")
        model = ret.strip()
        if len(model) > 0:
            ser.close()
            logger.info(f"Discovery {serial_port} -> {model}")

            return (serial_port, model)
            # data.append((serial_port, model))
        ser.close()
        return None
    except serial.SerialException:
        # If the port is already open, skip to the next one
        return None
    except OSError as e:
        print(e)
        return None


def discover() -> list:
    ports = list(serial.tools.list_ports.comports())
    data = []

    threads = []

    def check(port):
        return async_discover(port.device)

    for port in ports:
        thread = threading.Thread(
            target=lambda: data.append(async_discover(port.device)))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logger.info(data)
    data = list(filter(lambda x: x is not None, data))
    logger.info(data)
    return data


if __name__ == '__main__':
    discover()
