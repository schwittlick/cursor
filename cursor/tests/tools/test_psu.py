import random
import time

from cursor.device.psu import PSU


def DISABLED_test_psu():
    psu = PSU("/dev/ttyUSB5")
    psu.open()
    psu.set_voltage_limit(5)
    psu.set_current_limit(1)

    psu.on()
    for i in range(10):
        psu.set_voltage(random.uniform(0, 4))
        psu.set_current(1)
        time.sleep(1)

    psu.off()
