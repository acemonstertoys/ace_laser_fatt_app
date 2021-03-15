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

    def stringValue(self):
        if self is FilterType.GREEN_ORGANICS:
            return 'Organics'
        elif self is FilterType.WHITE_SYNTHETICS:
            return 'Synthetics'
        else:
            return 'Unknown'

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
        #print('Creating new Filter of type: '+ filterType.gcValue())
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        filter_API_URL = os.environ['ACEGC_BASE_URL'] + "/filters/"

        data = {
            'filter_type': filterType.gcValue(),
            'seconds_used': 0,
        }
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        resp = requests.post(filter_API_URL, data, headers=headers)
        #print(resp.content)
        jsonResp = resp.json()
        return cls(jsonResp['id'],filterType)

    @classmethod
    def fetch_existing_filters(cls):
        """
        Fetch existing filters from GC
        """
        print('Fetching existing Filters...')
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        filter_API_URL = os.environ['ACEGC_BASE_URL'] + "/filters/"
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        resp = requests.get(filter_API_URL, headers=headers)
        print(resp.content)
        filterJson = resp.json()
        filterList = list()
        for filterDict in filterJson:
            filterType = FilterType.GREEN_ORGANICS
            gcFilterType = filterDict['filter_type']
            if gcFilterType == "O":
                filterType = FilterType.GREEN_ORGANICS
            elif gcFilterType == "S":
                filterType = FilterType.WHITE_SYNTHETICS
            filterList.append(cls(filterDict['id'],filterType,filterDict['seconds_used']))
        return filterList

    def updateRuntime(self, currentOdometer):
        """
        docstring
        """
        usageTime = 0
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
        return self.filterType.stringValue(), self.calcRemainingTime()

    def display_id(self):
        """
        Prepends 'F' to the filterId, zero-padded to 3 characters
        """
        return 'F' + str(self.filterId).zfill(3)

    def display_summary(self):
        """
        Returns filter type and display_id() as a single string
        """
        return self.display_id() +" "+ self.filterType.stringValue()