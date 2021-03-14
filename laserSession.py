import os

class LaserSession:
    '''
    A user's laser session.
    '''

    def __init__(self, userDict, startingOdometer=0):
        self.credential = userDict['RFID']
        self.name = userDict['First Name'] + ' ' + userDict['Last Initial']
        self.startingOdometer = startingOdometer
        self.LASER_COST = os.environ.get('ACEGC_LASER_COST', 0.5)

    def calculate_firing_time(self, currentOdometer):
        """
        Subtracts the session starting odometer reading from the current odometer reading.
        """
        #TODO: document units
        print(currentOdometer)
        return int(currentOdometer) - self.startingOdometer
    
    def calculate_session_cost(self, currentOdometer):
        """
        Multiplies firing time by laser cost.
        Laser Cost is defined in the ACEGC_LASER_COST environment variable with a default of 0.5.
        Returns a currency formatted string
        """
        cost = self.calculate_firing_time(currentOdometer) / 60 * self.LASER_COST
        # format as currency string
        return "{:,.2f}".format(cost)
