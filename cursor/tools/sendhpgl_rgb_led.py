from argparse import ArgumentParser
from time import sleep

import serial
from serial import Serial
from tqdm import tqdm
import logging

from hpgl.hpgl_tokenize import tokenizer
from hpgl.plotter.plotter import HPGLPlotter

DEBUG = True


class RgbLedSerialSender:
    def __init__(self, serialport: str, serialport_arduino: str, hpgl_data: str):
        super().__init__(serialport, hpgl_data)

        self.commands = tokenizer(hpgl_data)

        self.plotter = HPGLPlotter(serial.Serial(serialport))
        self.port_arduino = Serial(serialport_arduino, baudrate=9600, timeout=1)

    def send(self):
        try:
            with tqdm(total=len(self.commands)) as pbar:
                pbar.update(0)
                for i in range(len(self.commands) - 1):
                    cmd = self.commands[i]
                    if cmd.startswith("PD"):
                        self.plotter.write(f"{cmd};")
                    elif cmd.startswith("PU"):
                        self.plotter.write(f"{cmd};")
                    elif cmd.startswith("PA"):
                        po = self.parse_pa(cmd)
                        self.send_and_wait(po)
                    elif cmd.startswith("PWM"):
                        pass
                        # parsed_pwm = int(re.findall(r'\d+', cmd)[0])
                        # current_pwm = parsed_pwm
                        # log.info(f"current_pwm: {parsed_pwm}")
                    elif cmd.startswith("VS"):
                        self.plotter.write(f"{cmd};")
                    pbar.update(1)

        except KeyboardInterrupt:
            logging.warning("Interrupted- aborting.")
            sleep(0.1)
            self.plotter.abort()

    def parse_pa(self, cmd) -> tuple[int, int]:
        pos = cmd[2:].split(',')
        po = (int(pos[0]), int(pos[1]))
        return po

    def send_and_wait(self, pp: tuple[int, int]):
        self.plotter.write(f"PA{pp[0]},{pp[1]};")
        self.poll(pp)

    def set_arduino_pwm(self, pwm: int):
        logging.info(f"set arduino pwm: {pwm}")
        self.port_arduino.write(f"{pwm}".encode('utf-8'))
        ret = self.port_arduino.readline()
        logging.info(f"arduino: {ret}")

    def poll(self, target_pos: tuple[int, int]):
        if DEBUG:
            return True

        current_po = self.plotter.get_position()

        attempts = 0
        while current_po != target_pos:
            current_po = self.plotter.get_position()
            attempts += 1
            sleep(0.1)

            if attempts > 20:
                return False
        return True


def main():
    parser = ArgumentParser()
    parser.add_argument('plotter')
    parser.add_argument('arduino')
    parser.add_argument('file')
    args = parser.parse_args()

    text = ''.join(open(args.file, 'r', encoding='utf-8').readlines())
    text = text.replace(" ", '').replace("\n", '').replace("\r", '')

    sender = RgbLedSerialSender(args.plotter, args.arduino, text)
    sender.send()


if __name__ == '__main__':
    main()
