import serial
import time
import wasabi

log = wasabi.Printer()


class DrawingMachine:
    def __init__(self):
        self.s = None
        self.ready = False

    def connect(self, port, baud):
        try:
            self.s = serial.Serial(port, baud)
            return True
        except serial.SerialException as se:
            self.s = None
            log.fail(se)
            return False

    def calib(self):
        self.s.write("\r\n\r\n".encode("utf-8"))
        time.sleep(2)  # Wait for grbl to initialize
        self.s.reset_input_buffer()

        self.kill_alarm()
        self.home()
        self.null_coords()

        self.ready = True

    def __send_and_print_reply(self, msg):
        assert self.s is not None, "No serial connection open"
        _msg = msg + "\n"
        log.warn(f"Sending {_msg}")
        self.s.write(_msg.encode("utf-8"))
        grbl_out = self.s.readline()  # Wait for grbl response with carriage return
        log.good(grbl_out.strip().decode("utf-8"))

    def feed_hold(self):
        self.__send_and_print_reply("!")

    def resume(self):
        self.__send_and_print_reply("~")

    def info(self):
        self.__send_and_print_reply("?")

    def kill_alarm(self):
        self.__send_and_print_reply("$X")

    def home(self):
        self.__send_and_print_reply("$H")

    def null_coords(self):
        self.__send_and_print_reply("G92X0Y0Z0")

    def stream(self, filename):
        assert self.s is not None, "No serial connection open"
        assert self.ready, "Not calibrated&homed, yet."

        file = open(filename, "r")
        for line in file:
            line = line.strip()
            self.__send_and_print_reply(line)

        # here should some kind of waiting happen.. for the machine to be done
        # checking the info() function and evaluating some stuff there
        # also the $10 in grbl config might have to be modified
        # https://github.com/gnea/grbl/wiki/Grbl-v1.1-Configuration#10---status-report-mask

        file.close()
        self.s.close()

    class Paper:
        X_FACTOR = 2.91666
        Y_FACTOR = 2.83333

        CUSTOM_36_48 = (360 * X_FACTOR, 480 * Y_FACTOR)
        CUSTOM_48_36 = (480 * X_FACTOR, 360 * Y_FACTOR)
        DIN_A1_LANDSCAPE = (841 * X_FACTOR, 594 * Y_FACTOR)
        DIN_A0_LANDSCAPE = (1189 * X_FACTOR, 841 * Y_FACTOR)

        @staticmethod
        def custom_36_48_portrait():
            return DrawingMachine.Paper.CUSTOM_36_48

        @staticmethod
        def custom_36_48_landscape():
            return DrawingMachine.Paper.CUSTOM_48_36

        @staticmethod
        def a1_landscape():
            return DrawingMachine.Paper.DIN_A1_LANDSCAPE

        @staticmethod
        def a0_landscape():
            return DrawingMachine.Paper.DIN_A0_LANDSCAPE
