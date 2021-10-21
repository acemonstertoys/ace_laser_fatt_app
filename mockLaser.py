
class MockLaser:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
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

