## plotters

    HP Draftmaster SX/HP7595A,
    HP7475A,
    Roland DG DXY-980,
    Roland DG DXY-990,
    Roland DG DXY-885,
    Roland DG DXY-1200,
    Tektronix 4662,
    Aritma 512,
    Roland DG DPX3300,
    Roland DG CAMM-1 PNC-1000,
    A0 DIY




##### HP 7595A & 7596A
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
    # turn auto button off (on machine)


#### Tektronix 4662
    baud 1200
    parity: none
    1 stop bit
    device A

You have to set the serial port config below every time you connect a serial/usb converter

    stty -F /dev/ttyUSB0 1200 cs8 -cstopb -parenb
    cat /path/to/file.tek > /dev/ttyUSB0

Joystick disconnected on the inside

#### GSI Digiplot A1

    baud 1200
    
    I; # pen down
    H; # pen up
    X100,Y100;
    X1000;I;K;H; # set coordinate, pen down, go absolute, pen up
    X/Y,10000,10000;K;  
    
    # calibrated a1 sheet 0,0 (bottom left)
    X,0;/Y,0;K;  
    # and top right
    X,33600;/Y,23700;K;    

    # min/max Y
    /Y,0;K;
    /Y,27500;K;
    
    # min/max x
    X/,-8000;K;
    X,34000;K;

    # both min/max
    X,-8000;/Y,0;K;
    X,35000;/Y,27500;K;

    python sendhpgl.py /dev/ttyUSB0 1200 0 ~/../plot/digii/None_simple_rect_example_simple_rect_landscape_a1_digiplot_a1_1dbf7144266374ee479325f40560b78250e73b321b75a7b63d2d1147160e00cc.digi 


#### HP 7470A

    OH; does not work..
    don't use null modem
    baud 9600
    draw in portrait mode
    this model does not fedback anything
    also limited hpgl capability
    python tools/serial_sender.py /dev/ttyUSB1 9600 0 data/experiments/simple_rect_example/hpgl/simple_rect_example_simple_rect_landscape_a4_hp7470a_26af20deac7561081a545151d62d83c33204365e42bb30050af6c3cb5a81082d_None.hpgl 
