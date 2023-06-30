import random
import time
import typing

import serial


class PSU:
    """
    Control a Kiprim DC310S lab power supply
    """

    STATUS = "*IDN?"
    VOLT = "VOLTage"
    CURRENT = "CURRent"
    VOLT_LIMIT = "VOLTage:LIMit"
    CURRENT_LIMIT = "CURRent:LIMit"
    ONOFF = "OUTPut"

    def __init__(self, port):
        self.__serial = serial.Serial()
        self.__baudrate = 115200
        self.__port = port

    def __send(self, prefix: str, value: typing.Union[int, float] = None) -> None:
        if not self.__serial.is_open:
            raise Exception("Serial port not connected")

        if value is None:
            self.__serial.write(f"{prefix}\n".encode())

        if isinstance(value, int):
            self.__serial.write(f"{prefix} {value}\n".encode())

        if isinstance(value, float):
            self.__serial.write(f"{prefix} {value:.3}\n".encode())

    def __read(self) -> str:
        return self.__serial.readline().decode()

    def open(self) -> bool:
        self.__serial = serial.Serial(self.__port, baudrate=self.__baudrate, timeout=1)
        self.__send(PSU.STATUS)
        status = self.__read()
        return len(status) > 0

    def close(self) -> None:
        self.__serial.close()

    def on(self) -> None:
        self.__send(PSU.ONOFF, 1)

    def off(self) -> None:
        self.__send(PSU.ONOFF, 0)

    def set_voltage_limit(self, volts: float) -> None:
        self.__send(PSU.VOLT_LIMIT, volts)

    def set_current_limit(self, amps: float) -> None:
        self.__send(PSU.CURRENT_LIMIT, amps)

    def set_voltage(self, volts: float) -> None:
        self.__send(PSU.VOLT, volts)

    def set_current(self, amps: float) -> None:
        self.__send(PSU.CURRENT, amps)


if __name__ == '__main__':
    psu = PSU("COM10")
    psu.open()
    psu.set_voltage_limit(5)
    psu.set_current_limit(1)

    psu.on()
    for i in range(10):
        psu.set_voltage(random.uniform(0, 4))
        psu.set_current(1)
        time.sleep(1)

    psu.off()
