from argparse import ArgumentParser

from serial import Serial

from cursor.hpgl.analyze import HPGLAnalyzer
from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.hpgl.plotter.plotter import HPGLPlotter
from cursor.tools.serial_powertools.seriallib import SerialSender


def main():
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    args = parser.parse_args()

    analyzer = HPGLAnalyzer()
    analyzer.analyze(args.file)

    text = ''.join(open(args.file, 'r', encoding='utf-8').readlines())
    # text = text.replace(" ", '').replace("\n", '').replace("\r", '')

    commands = tokenizer(text)

    serial = Serial(port=args.port, baudrate=9600, timeout=1)
    plotter = HPGLPlotter(serial)

    sender = SerialSender()
    sender.send(plotter, commands)


if __name__ == '__main__':
    pass
