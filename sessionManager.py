from datetime import datetime
from enum import Enum
from filter import Filter, FilterType
from laserSession import LaserSession
import os
import requests
import sys

# Global Variables ----
class Auth_Result(Enum):
    NOT_AUTHENTICATED = 0
    AUTHENTICATED = 1
    LOGGED_OUT = 2
    ANOTHER_USER_LOGGED_IN = 3
    ERROR = 4

class SessionManager:
    def __init__(self, currentUser=None, currentFilter=None):
        # Instance variables
        self.currentUser = currentUser
        self.currentFilter = currentFilter

    # Filter Methods
    def currentFilterData(self):
        """
        Returns filter type and time remaining on filter
        """
        if self.currentFilter != None:
            return self.currentFilter.filterSummary()
        else:
            return 'Unknown', 0

    def isFilterChangeNeeded(self):
        """
        docstring
        """
        if self.currentFilter == None:
            return True
        elif self.currentFilter.calcRemainingTime() < 10:
            return True
        else:
            return False
    
    def createNewFilter(self, filterType):
        """
        docstring
        """
        self.currentFilter = Filter(filterType)
        #TODO call GC to generate filterId

    # Authentication Methods
    def authenticate_credential(self, credential):
        result = Auth_Result.NOT_AUTHENTICATED
        if self.currentUser == None:
            authSuccess = False
            rfids = self.fetchAccessList()
            if credential in rfids:
                self.currentUser = LaserSession(credential)
                result = Auth_Result.AUTHENTICATED
                authSuccess = True
            self.postActivityListing(credential,authSuccess)
        elif self.currentUser.credential == credential:
            self.logout(credential)
            result = Auth_Result.LOGGED_OUT
        else:
            result = Auth_Result.ANOTHER_USER_LOGGED_IN
        return result

    def logout(self, credential):
        self.currentUser = None
        #TODO log to GC LaserActivty
   
    def fetchAccessList(self):
        """
        Pulls certified laser RFIDs from URL defined as an environment variable
        """
        print("fetching access list...")
        laserAccessURL = os.getenv("ACE_ACCESS_URL")

        payload = None
        headers = {'User-Agent': 'Wget/1.20.1 (linux-gnu)'}
        try:
            # response = requests.get(laserAccessURL, params=payload, verify=False)
            response = requests.get(laserAccessURL, params=payload, headers=headers)
        except requests.exceptions.Timeout:
            #TODO  Maybe set up for a retry, or continue in a retry loop
            print("Timeout connecting to URL")
            sys.exit(1)
        except requests.exceptions.TooManyRedirects:
            #TODO Tell the user their URL was bad and try a different one
            print("Invalid URL, exiting")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        rfids = response.content.decode("utf-8").split('\n')
        # cache rfids
        file = open("authorized.txt", "w+")
        for token in rfids:
            # short_token = token[-6:]
            short_token = token[-8:]
            file.write(short_token + "\n")
        return rfids

    def load_acceslist(self):
        with open("authorized.txt", 'r') as f:
            authorized_rfids = f.read().split("\n")
            return authorized_rfids

    def postActivityListing(self, credential, authSuccess):
        print('posting ActivityListing for '+ credential, authSuccess)
        ASSET_ID = os.environ['ACEGC_ASSET_ID']
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        REPORTING_URL = os.environ['ACEGC_REPORTING_URL']

        data = {
            'access_point': ASSET_ID,
            'activity_date': datetime.now(),
            'credential': credential,
            'success': authSuccess,
        }
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        resp = requests.post(REPORTING_URL, data, headers=headers)
        print(resp.content)
        return resp