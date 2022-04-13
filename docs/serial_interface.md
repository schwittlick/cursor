### Tektronix 4662
You have to set the serial port config below every time you connect a serial/usb converter

    stty -F /dev/ttyUSB0 1200 cs8 -cstopb -parenb
    cat /path/to/file.tek > /dev/ttyUSB0