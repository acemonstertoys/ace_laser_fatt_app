class LaserSession:
    def __init__(self, credential, firstName='User', startingOdometer=0):
        self.credential = credential
        self.firstName = firstName
        self.startingOdometer = startingOdometer
        self.currentOdometer = startingOdometer

    def calculate_firing_time():
        """
        docstring
        """
        return self.currentOdometer - self.startingOdometer
    
    def calculate_session_cost():
        """
        docstring
        """
        #TODO pull from laser.py
        return 0.0
