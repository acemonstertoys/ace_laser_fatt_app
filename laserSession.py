class LaserSession:
    def __init__(self, userDict, startingOdometer=0):
        self.credential = userDict['RFID']
        self.name = userDict['First Name'] + ' ' + userDict['Last Initial']
        self.startingOdometer = startingOdometer
        self.currentOdometer = startingOdometer

    def calculate_firing_time(this):
        """
        docstring
        """
        return self.currentOdometer - self.startingOdometer
    
    def calculate_session_cost(this):
        """
        docstring
        """
        #TODO pull from laser.py
        return 0.0
