import serial
import time
import wasabi
from kivy.clock import Clock

log = wasabi.Printer()


class DrawingMachine:
    def __init__(self):
        self.__serial = None
        self.__error = False
        self.__ready = False

    def ready(self):
        if self.__ready and not self.__error:
            return True
        log.warn(f"Not ready. ready={self.__ready}, error={self.__error}")
        return False

    def connect(self, port, baud):
        if self.__serial:
            log.warn("Can't connect when already connected")
            return
        try:
            self.__serial = serial.Serial(port, baud, timeout=5)
            log.good(f"Connected to {port}:{baud}.")
            return True
        except serial.SerialException as se:
            self.__serial = None
            log.fail(se)
            return False

    def disconnect(self):
        if self.__serial is None:
            log.warn(f"Can't disconnect when not connected")
            return

        if not self.__serial.is_open:
            log.warn(f"Can't disconnect when not connected")
            return

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.close()
        self.__serial = None

    def connected(self):
        if self.__serial is not None:
            return self.__serial.is_open

        return False

    def calib(self):
        self.__send_and_print_reply("\r\n\r", 2)
        self.__serial.reset_input_buffer()

        self.kill_alarm()
        self.home()
        self.null_coords()

        self.__ready = True

    def __send_and_print_reply(self, msg, delay=0):
        if self.__error:
            log.warn(f"Not sending {msg} because an error occurred.")
            return

        if self.__serial is None:
            log.warn(f"Can't send when not connected")
            return

        _msg = msg + "\n"
        log.good(f"Sending {_msg}")
        self.__serial.write(_msg.encode("utf-8"))
        time.sleep(delay)
        grbl_out = self.__serial.readline()
        try:
            result = grbl_out.strip().decode("utf-8")
            if "ok" in result:
                log.good(result)
                return True, result
            elif "error" in result:
                log.fail(result)
                return False, result
            else:
                log.fail(result)
                return False, result
        except Exception as e:
            log.fail(f"Failed to receive anything for input: {_msg}. {e}")
            self.__error = True
            return False, f"ERROR: {e}"

    def feed_hold(self):
        self.__send_and_print_reply("!")

    def resume(self):
        self.__send_and_print_reply("~")

    def info(self):
        return self.__send_and_print_reply("?")

    def kill_alarm(self):
        self.__send_and_print_reply("$X")

    def home(self):
        self.__send_and_print_reply("$H")

    def null_coords(self):
        self.__send_and_print_reply("G92X0Y0Z0")

    def stream(self, filename):
        if self.__serial is None:
            log.warn(f"Can't stream when not connected")
            return

        if not self.__ready:
            log.warn(f"Can't stream when not calibrated & homed")
            return

        file = open(filename, "r")
        lines = file.readlines()
        file.close()

        i = 0
        while i < len(lines):
            line = lines[i]
            log.good(f"i={i}")
            success, msg = self.__send_and_print_reply(line)
            if not success:
                log.warn(f"Not Successful")
            else:
                i += 1
        #for line in lines:
        #    line = line.strip()
        #    success = self.__send_and_print_reply(line)

        # here should some kind of waiting happen.. for the machine to be done
        # checking the info() function and evaluating some stuff there
        # also the $10 in grbl config might have to be modified
        # https://github.com/gnea/grbl/wiki/Grbl-v1.1-Configuration#10---status-report-mask

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
