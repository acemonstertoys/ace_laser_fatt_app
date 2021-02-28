from enum import Enum, auto
import os
import requests

# Global Variables ----
''' How many minutes should a filter be used? '''
GREEN_ORGANICS_LIFE = 140
WHITE_SYNTHETICS_LIFE = 60

class FilterType(Enum):
    GREEN_ORGANICS = auto()
    WHITE_SYNTHETICS = auto()

    def gcValue(self):
        if self is FilterType.GREEN_ORGANICS:
            return 'O'
        elif self is FilterType.WHITE_SYNTHETICS:
            return 'S'
        else:
            return 'U'

class Filter:
    """
    How to change the filter before the blower
    https://wiki.acemakerspace.org/how-to-change-the-filter-before-the-blower/
    """

    def __init__(self, filterId, filterType, recordedUsage=0, odometerReading=0):
        self.filterId = filterId
        self.filterType = filterType
        self.recordedUsage = recordedUsage
        self.startOdometer = odometerReading    # what units is the odometer in?
        self.endOdometer = odometerReading

    @classmethod
    def create_new_filter(cls, filterType):
        """
        Creates a new filter in GC
        """
        print('Creating new Filter of type: '+ filterType.gcValue())
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        filter_API_URL = os.environ['ACEGC_BASE_URL'] + "/filters/"

        data = {
            'filter_type': filterType.gcValue(),
            'seconds_used': 0,
        }
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        resp = requests.post(filter_API_URL, data, headers=headers)
        print(resp.content)
        jsonResp = resp.json()
        return cls(jsonResp['id'],filterType)

    def changeFilter(self, oldFilterID, newFilterID):
        """
        docstring
        """
        self.updateRuntime()
        pass

    def updateRuntime(self, usageTime):
        """
        docstring
        """
        #TODO call GC
        pass

    def calcRemainingTime(self):
        """
        Green organics filters can be used for a total of 140 minutes.
        White synthetics filter can be used for a total of 60 minutes.
        """
        #print('calcRemainingTime for Filter of type: '+ self.filterType.gcValue())
        currentUsage = self.endOdometer - self.startOdometer
        totalUsage = self.recordedUsage + currentUsage
        remainingTime = 0
        if self.filterType == FilterType.GREEN_ORGANICS:
            remainingTime = GREEN_ORGANICS_LIFE - totalUsage
        elif self.filterType == FilterType.WHITE_SYNTHETICS:
            remainingTime = WHITE_SYNTHETICS_LIFE - totalUsage
        #print("calcRemainingTime: "+str(remainingTime))
        return remainingTime

    def filterSummary(self):
        """
        Returns filter type and time remaining on filter
        """
        filterType = 'Unknown'
        remainingTime = self.calcRemainingTime()
        if self.filterType == FilterType.GREEN_ORGANICS:
            filterType = "Organics"
        elif self.filterType == FilterType.WHITE_SYNTHETICS:
            filterType = "Synthetics"
        return filterType, remainingTime

    def display_id(self):
        """
        Prepends 'F' to the filterId, zero-padded to 3 characters
        """
        return 'F' + str(self.filterId).zfill(3)