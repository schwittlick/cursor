from cursor.device import DrawingMachine


def main():
    m = DrawingMachine()
    m.connect("COM4", 115200)
    m.calib()


if __name__ == "__main__":
    main()
