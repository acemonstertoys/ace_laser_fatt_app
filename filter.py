from enum import Enum
import requests

# Global Variables ----
''' How many minutes should a filter be used? '''
GREEN_ORGANICS_LIFE = 140
WHITE_SYNTHETICS_LIFE = 60

class FilterType(Enum):
    GREEN_ORGANICS = 0
    WHITE_SYNTHETICS = 1

class Filter:
    """
    How to change the filter before the blower
    https://wiki.acemakerspace.org/how-to-change-the-filter-before-the-blower/
    """

    def __init__(self, filterType, filterId=0, odometerReading=0):
        self.filterId = filterId
        self.filterType = filterType
        self.recordedUsage = 0
        self.startOdometer = odometerReading    # what units is the odometer in?
        self.endOdometer = odometerReading

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
        currentUsage = self.endOdometer - self.startOdometer
        totalUsage = self.recordedUsage + currentUsage
        if self.filterType == FilterType.GREEN_ORGANICS:
            remainingTime = GREEN_ORGANICS_LIFE - totalUsage
        elif self.filterType == FilterType.WHITE_SYNTHETICS:
            remainingTime = WHITE_SYNTHETICS_LIFE - totalUsage
        return remainingTime

    def filterSummary(self):
        """
        Returns filter type and time remaining on filter
        """
        filterType = 'Unknown'
        remainingTime = self.calcRemainingTime()
        if self.filterType == FilterType.GREEN_ORGANICS:
            filterType = "Organics"
        else:
            filterType = "Synthetics"
        return filterType, remainingTime
