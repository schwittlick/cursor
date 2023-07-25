from argparse import ArgumentParser
from time import sleep

import wasabi
from serial import Serial
from tqdm import tqdm
import re

from cursor.hpgl import read_until_char
from cursor.hpgl.sendhpgl import SerialSender
from tools.psu import PSU

log = wasabi.Printer(pretty=True)

DEBUG = True


class LaserSerialSender(SerialSender):
    def __init__(self, serialport: str, serialport_arduino: str, serialport_psu, hpgl_data: str):
        super().__init__(serialport, hpgl_data)

        self.port_arduino = Serial(serialport_arduino, baudrate=9600, timeout=1)
        self.psu = PSU(serialport_psu)
        self.psu.open()
        self.psu.set_voltage_limit(5)
        self.psu.set_current_limit(1)
        self.psu.off()

        sleep(1)
        d = self.port_arduino.readline()
        log.info(f"first arduino result: {d}")
        sleep(1)

        self.set_arduino_pwm(0)

    def send(self):
        try:
            with tqdm(total=len(self.commands)) as pbar:
                pbar.update(0)

                current_pwm = 0
                current_delay = 0

                for i in range(len(self.commands) - 1):
                    cmd = self.commands[i]
                    next_cmd = self.commands[i + 1]

                    if cmd.startswith("PD"):
                        self.set_arduino_pwm(current_pwm)  # turn on previously configured pwm
                        self.psu.on()
                        sleep(current_delay)
                        current_delay = 0
                        self.plotter.write(f"{cmd};".encode('utf-8'))
                    elif cmd.startswith("PU"):
                        self.set_arduino_pwm(0)  # off when pen up
                        self.psu.off()
                    elif cmd.startswith("PA"):
                        if DEBUG:
                            log.info(f"{cmd}")

                        po = self.parse_pa(cmd)
                        self.send_and_wait(po)

                        if next_cmd.startswith("PD"):
                            # time.sleep(0.5)
                            little_off = (po[0] + 10, po[1] + 10)
                            self.send_and_wait(little_off)
                    elif cmd.startswith("PWM"):
                        parsed_pwm = int(re.findall(r'\d+', cmd)[0])
                        current_pwm = parsed_pwm
                        log.info(f"current_pwm: {parsed_pwm}")
                    elif cmd.startswith("VOLT"):
                        volt = float(cmd[4:-1])
                        self.psu.set_voltage(volt)
                        pass
                    elif cmd.startswith("DELAY"):
                        current_delay = float(cmd[5:-1])
                        pass
                    elif cmd.startswith("VS"):
                        log.info(f"{cmd}")
                        self.plotter.write(f"{cmd};".encode('utf-8'))
                    pbar.update(1)
        except KeyboardInterrupt:
            log.warn("Interrupted- aborting.")
            sleep(0.1)
            self.abort()

    def parse_pa(self, cmd) -> tuple[int, int]:
        pos = cmd[2:].split(',')
        po = (int(pos[0]), int(pos[1]))
        return po

    def send_and_wait(self, pp: tuple[int, int]):
        self.plotter.write(f"PA{pp[0]},{pp[1]};".encode('utf-8'))
        self.poll(pp)

    def set_arduino_pwm(self, pwm: int):
        log.info(f"set arduino pwm: {pwm}")
        self.port_arduino.write(f"{pwm}".encode('utf-8'))
        ret = self.port_arduino.readline()
        log.info(f"arduino: {ret}")

    def poll(self, target_pos: tuple[int, int]):
        if DEBUG:
            return True

        self.plotter.write('OA;'.encode('utf-8'))
        ret = read_until_char(self.plotter).rstrip()
        if len(ret) == 0:
            return False
        current_pos = ret.split(',')
        current_po = (int(current_pos[0]), int(current_pos[1]))

        attempts = 0
        while current_po != target_pos:
            self.plotter.write('OA;'.encode('utf-8'))
            ret = read_until_char(self.plotter).rstrip()
            if len(ret) == 0:
                attempts += 1
                continue

            if ',' not in ret:
                attempts += 1
                continue

            current_pos = ret.split(',')
            current_po = (int(current_pos[0]), int(current_pos[1]))

            sleep(0.1)

            if attempts > 20:
                return False
        return True


def main():
    parser = ArgumentParser()
    parser.add_argument('plotter')
    parser.add_argument('arduino')
    parser.add_argument('psu')
    parser.add_argument('file')
    args = parser.parse_args()

    text = ''.join(open(args.file, 'r', encoding='utf-8').readlines())
    text = text.replace(" ", '').replace("\n", '').replace("\r", '')

    sender = LaserSerialSender(args.plotter, args.arduino, args.psu, text)
    sender.send()


if __name__ == '__main__':
    main()
