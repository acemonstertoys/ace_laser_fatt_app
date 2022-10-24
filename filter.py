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
        self.startOdometer = odometerReading    # units is the odometer are in is Seconds
        self.endOdometer = odometerReading

    @classmethod
    def create_new_filter(cls, filterType, odoValue):
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
        resp = requests.post(filter_API_URL, data, headers=headers, timeout=5)
        #print(resp.content)
        jsonResp = resp.json()
        return cls(jsonResp['id'],filterType, odometerReading=odoValue)

    @classmethod
    def fetch_existing_filters(cls):
        """
        Fetch existing filters from GC
        """
        print('Fetching existing Filters...')
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        filter_API_URL = os.environ['ACEGC_BASE_URL'] + "/filters/"
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        resp = requests.get(filter_API_URL, headers=headers, timeout=5)
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

    def updateRuntime(self):
        """
        Calculates usage and posts it to GC
        """
        print('Filter updateRuntime...')
        currentUsage = self.endOdometer - self.startOdometer
        if currentUsage > 0:
            totalUsage = self.recordedUsage + currentUsage
            # update GC
            GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
            filter_API_URL = os.environ['ACEGC_BASE_URL'] +"/filters/"+ str(self.filterId) +"/"
            headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
            data = {
                'seconds_used': totalUsage,
            }
            resp = requests.patch(filter_API_URL, data, headers=headers, timeout=5)
            print(resp.content)
            self.recordedUsage = totalUsage
            self.startOdometer = self.endOdometer

    def retire(self):
        """
        Update is_retired flag on GC
        """
        print('retiring filter... id = %d' % (self.filterId))
        # update GC
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        filter_API_URL = os.environ['ACEGC_BASE_URL'] +"/filters/"+ str(self.filterId) +"/"
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        data = {
            'is_retired':True
        }
        resp = requests.patch(filter_API_URL, data, headers=headers, timeout=5)
        print(resp.content)

    def calcRemainingTime(self):
        """
        Green organics filters can be used for a total of 140 minutes.
        White synthetics filter can be used for a total of 60 minutes.
        """
        print('calcRemainingTime for Filter of type: '+ self.filterType.gcValue())
        currentUsage = self.endOdometer - self.startOdometer
        totalUsageMin = (self.recordedUsage + currentUsage)/60
        remainingTime = 0
        if self.filterType == FilterType.GREEN_ORGANICS:
            remainingTime = GREEN_ORGANICS_LIFE - totalUsageMin
        elif self.filterType == FilterType.WHITE_SYNTHETICS:
            remainingTime = WHITE_SYNTHETICS_LIFE - totalUsageMin
        print("calcRemainingTime: "+str(remainingTime))
        return remainingTime

    def shouldBeRetired(self):
        print('checking shouldBeRetired for Filter: '+ self.display_id())
        return self.calcRemainingTime() < 10

    def filterSummary(self):
        """
        Returns filter summary and time remaining
        """
        return self.display_summary(), self.calcRemainingTime()

    def display_id(self):
        """
        Prepends 'F' to the filterId, zero-padded to 3 characters
        """
        return 'F' + str(self.filterId).zfill(3)

    def display_summary(self):
        """
        Returns display_id() and filter type as a single string
        """
        return self.display_id() +" "+ self.filterType.stringValue()

    def display_full_summary(self):
        """
        Returns display_id(), filter type and time remaining as a single string
        """      
        return self.display_id() +" "+ self.filterType.stringValue() +" ("+ str(round(self.calcRemainingTime())) +" Min.)"
