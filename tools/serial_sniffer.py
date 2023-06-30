import serial
import time

if __name__ == '__main__':
    """
    Used a virtual serial port to connect COM1 <-> COM2
    The PSU is connected via USB, turned on and is COM10
    1. start this script
    2. Connect iPowerControl to COM1
    3. Watch the outputs happen to reverse engineer the protocol

    *IDN? -> init
    MEASure:VOLTage? -> return voltage
    MEASure:CURRent? -> current current
    OUTPut? -> is it on?

    VOLTage 0.000 -> set voltage
    CURRent 0.000 -> set current
    OUTPut 1 -> set on
    OUTPut 0 -> set off

    CURR:LIM? MAX -> get max curr
    CURR:LIM? MIN
    CURR? MIN
    CURR? MAX

    VOLTage:LIMit 5.000 -> set volt limit
    CURRent:LIMit 2.000 -> set current limit
    """

    serial_ipowercontrol = serial.Serial('COM2', 9600)
    serial_psu = serial.Serial('COM10', 115200)
    while True:
        try:
            if serial_psu.in_waiting > 0:
                data = serial_psu.readline().decode('utf-8').strip()
                print('Received from PSU:', data)

                serial_ipowercontrol.write(f"{data}\n".encode('utf-8'))

            if serial_ipowercontrol.in_waiting > 0:
                data = serial_ipowercontrol.readline().decode('utf-8').strip()

                print('Received from iPowerControl:', data)

                serial_psu.write(f"{data}\n".encode('utf-8'))

            time.sleep(0.01)

        except KeyboardInterrupt:
            print("Exiting program.")
            break

        except Exception as e:
            print("Error:", str(e))

    serial_ipowercontrol.close()
    serial_psu.close()
