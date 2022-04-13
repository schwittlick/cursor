
##### HP7595A
    - serial cable with usb adapter
    - ohne nullmodem
    - sendhpgl port file
    - inkscape hpgl export check "centerd"

##### HP7475A
    - serial cable with usb adapter
    - mit nullmodem
    - sendhpgl port file
    - https://github.com/b4ckspace/hpgl-plot

##### HP7475A buffer overflow
    - serial cable with usb adapter
    - mit null modem
    - cat file to port

#### HP7475A inkscape
    - document layout: A3 in landscape 
    - export hpgl not centered

#### Roland CAMM-1
    - usb to parallel port adapter
    - chmod 777 /dev/usb/lp0
    - cat file.hpgl /dev/usb/lp0

#### HP7475a GPIB HPIB
    https://pearl-hifi.com/06_Lit_Archive/15_Mfrs_Publications/20_HP_Agilent/HP_7475A_Plotter/HP_7475A_Op_Interconnect.pdf
    - Prologix GPIB Configurator
    - Auf ID 5
    - Arduino Serial Monitor, "help++"
    http://prologix.biz/downloads/PrologixGpibUsbManual-6.0.pdf

##### Roland DPX3300
usb to parallel port adapter

    chmod 777 /dev/usb/lp0
    cat file.hpgl /dev/usb/lp0


#### Tektronix 4662
    baud 1200
    parity: none
    1 stop bit
    device A

You have to set the serial port config below every time you connect a serial/usb converter

    stty -F /dev/ttyUSB0 1200 cs8 -cstopb -parenb
    cat /path/to/file.tek > /dev/ttyUSB0

Joystick disconnected on the inside
