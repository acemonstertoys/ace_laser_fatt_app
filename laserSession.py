import os
from datetime import datetime


class LaserSession:
    '''
    A user's laser session.
    '''

    def __init__(self, userDict, startingOdometer=0):
        self.credential = userDict['RFID']
        self.name = userDict['First Name'] + ' ' + userDict['Last Initial']
        self.member_id = userDict['UID']
        self.start_odo = startingOdometer
        self.end_odo = startingOdometer
        self.LASER_COST = os.environ.get('ACEGC_LASER_COST', 0.5)
        self.start_time = datetime.now()
        self.end_time = datetime.now()

    def calculate_firing_time(self):
        """
        Subtracts the session starting odometer reading from the current odometer reading.
        """
        #TODO: document units
        return self.end_odo - self.start_odo
    
    def calculate_session_cost(self):
        """
        Multiplies firing time by laser cost.
        Laser Cost is defined in the ACEGC_LASER_COST environment variable with a default of 0.5.
        Returns a currency formatted string
        """
        cost = self.calculate_firing_time() / 60 * self.LASER_COST
        # format as currency string
        return "{:,.2f}".format(cost)
