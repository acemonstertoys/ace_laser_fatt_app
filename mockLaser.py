
class MockLaser:
    '''
    MockLaser used in place of Laser for development purposes only.
    SessionManager will instantiate MockLaser if the environment vairable LASERGUI_MOCK exists. 
    '''
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        print("Initializing MockLaser...")
        self.port = port
        self.baudrate= baudrate
        self.enabled = False
        self.odometer = '0'

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def status(self):
        self.odometer = '0'
