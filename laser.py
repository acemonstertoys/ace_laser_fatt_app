import time
import serial

class Laser:
    '''
    The pi interfaces with the laser through a Teensy connected via a USB port.  
    The Teensy responds to binary encoded ascii characters, and sends binary encoded ascii strings.  
    The interface is documented here: https://github.com/acemonstertoys/laser-rfid
    The USB port needs to be reset on initialization to capture it. 
    This requires writing to the USB_PATH as root.
    The Teensy itself runs firmware from the same repo as above.
    The Teensy responds to a status command 'o' with the current time
    it's been firing and a flag indiciating a new rfid scan.
    The Teensy state is reported as 'current firiing time since last reset' and 'new rfid scan'.
    If there has been a new scan, the Teensy will send the ID following a 'r' command.
    The pi needs to manage the implications of the state (e.g. an increase in
    firing time indicates the laser has been on, and the pi determines if the
    rfid token is authorized.)
    The laser is a reporting a simple state when polled.  
    So the pi must continually poll the laser state and manage it's authorization state.
    :param port: system serial port path
    :type port: string
    :param baudrate: serial port baudrate
    :type baudrate: int
    '''
    USB_PATH = "/sys/bus/usb/devices/usb1/authorized"
    # would prefer if the Teensy weren't so opinionated about what to do.
    # why save to eeprom when you can just send information about if the
    # laser is firing to the rpi and save it there?
    # Why using such a slow baudrate?  ATTINYs are fast.

    LASER_COST = 0.5

    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        self.reset_usb()
        time.sleep(1)
        self.conn = serial.Serial(port, baudrate)
        self.disable()
        self.odometer = '0'
        self.rfid_flag = '0'
        self.status()

    def write_raw(self, msg):
        self.conn.reset_input_buffer()
        self.conn.write(msg)

    def write(self, msg):
        self.write_raw(bytes('{}\n'.format(msg), 'ascii'))

    def read_raw(self):
        # default terminator is '\n' but explict is good
        return self.conn.read_until(b'\n')

    def read(self):
        ''' Grabs data from the serial port, decodes, and strips protocol
        control chars, currently '\n'.  This function should be used rather
        than reading hte Sesrial connection directly for uniformity.
        '''
        more = True
        data = b''
        while more:
            data += self.read_raw()
            if self.conn.in_waiting <= 0:
                more = False
        if data:
            return data.decode('ascii').strip('\n')
        else:
            return ''

    def enable(self):
        ''' Enables the laser through Teensy '''
        self.write("e")
        self.enabled = True

    def disable(self):
        ''' Disable the laser through Teensy '''
        self.write("d")
        self.enabled = False

    def reset_usb(self):
        ''' Resets the USB port, specific to sysfs paths'''
        with open(self.USB_PATH, 'w') as f:
            f.write('0')
            time.sleep(1)
            f.write('1')

    # deprecated 
    def display(self, line1='', line2=''):
        ''' Displays on the 2-line VCD display connected to Teesy '''
        if line1:
            self.write('p'+line1)
        if line2:
            self.write('q'+line2)

    def status(self):
        ''' Reads status from the laser, which is a string
        'o{cut_time}x{rfid_flag}'
        cut_time is how long the laser has been firing for
        rfid_flag indicates if a swipe was done
        '''
        self.write('o')
        data = self.read()
        if data:
            try:
                self.odometer, self.rfid_flag = data[1:].split('x')
            except (IndexError, TypeError) as e:
                print("{}: status - {}".format(e, data))

    # deprecated 
    def rfid(self):
        ''' requests rfid string from Teensy, returns 8 bits only.  For
        compatibility, can use 8bit or 10bits.
        '''
        self.write("r")
        time.sleep(.1)
        data = self.read()[1:]
        if len(data) == 8:
            return data
        if len(data) == 10:
            return data[2:]

    def reset_cut_time(self):
        ''' Part of Teensy laser interface.  Resets odometer on teensy'''
        self.write('x')

    def update_cut_time(self):
        ''' Explicit update of odometer'''
        self.write('y')

    def read_cut_time(self):
        ''' Retrieve odometer from Teensy'''
        self.write('z')

    def cost(self, firing_time):
        return firing_time / 60 * LASER_COST

    def reset(self):
        self.disable()
        self.reset_cut_time()
