from datetime import datetime
from enum import Enum
from filter import Filter, FilterType
from laser import Laser
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
        self.laserInterface = Laser()
        self.laserInterface.disable()

    def currentOdometer(self):
        """
        Fetch the current odometer from the Laser
        """
        self.laserInterface.status()
        # the laser interface stores the odometer reading as a string
        odoInt = int(self.laserInterface.odometer)
        if self.currentUser != None:
            self.currentUser.end_odo = odoInt
        if self.currentFilter != None:
            self.currentFilter.endOdometer = odoInt
        return odoInt
    
    # Filter Methods
    def currentFilterData(self):
        """
        Returns filter type and time remaining on filter
        """
        if self.currentFilter != None:
            return self.currentFilter.filterSummary()
        else:
            return 'Unknown', 0

    def is_filter_change_needed(self):
        """
        docstring
        """
        if self.currentFilter == None:
            return True
        elif self.currentFilter.calcRemainingTime() < 10:
            return True
        else:
            return False
    
    def create_new_filter(self, filterType):
        """
        Calls Filter to create new filter
        """
        self.currentFilter = Filter.create_new_filter(filterType, self.currentOdometer())

    def fetch_existing_filters(self):
        """
        Calls class method on Filter to Fetch existing filters from GC
        """
        return Filter.fetch_existing_filters()

    def switch_to_filter(self, filterObj):
        """
        updates the runtime on the current filter before switching to the passed in the filter
        """
        odoValue = self.currentOdometer()
        filterObj.startOdometer = odoValue
        filterObj.endOdometer = odoValue
        if self.currentFilter != None:
            # update current filter usage time
            self.currentFilter.updateRuntime()
        self.currentFilter = filterObj

    # Authentication Methods
    def authenticate_credential(self, credential):
        """
        Called when a fob is tagged.
        """
        result = Auth_Result.NOT_AUTHENTICATED
        if self.currentUser == None:
            authSuccess = False
            self.currentUser = self.authorized_user_for_credential(credential)
            if self.currentUser != None:
                result = Auth_Result.AUTHENTICATED
                authSuccess = True
                self.laserInterface.enable()
            self.postActivityListing(credential,authSuccess)
        elif self.currentUser.credential == credential:
            self.logout(credential)
            result = Auth_Result.LOGGED_OUT
        else:
            result = Auth_Result.ANOTHER_USER_LOGGED_IN
        return result
    
    def authorized_user_for_credential(self, credential):
        """
        Looks for the credential, aka fob, in the access list.
        The access list is a json list of laser authorized user disctionaries.
        Each user dictionary should contain an RFID key, the credential.
        Returns a LaserSession representing the user or none if no match
        """
        print('checking for credential: '+ credential +' in access list...')
        user = None
        accessList = self.fetch_access_list()
        for userDict in accessList:
            #print(ususerDicter)
            if userDict['RFID'] == credential:
                print('found!')
                user = LaserSession(userDict, self.currentOdometer())
                break
        return user

    def logout(self, credential):
        self.laserInterface.disable()
        self.currentUser.end_time = datetime.now()
        self.currentOdometer()
        # log laser activity to GC
        self.postLaserSession(self.currentUser)
        self.currentUser = None
   
    def fetch_access_list(self):
        """
        Pulls certified laser RFIDs from URL defined as an environment variable.
        The json list contains only those user allowed to use the laser.
        """
        print("fetching access list...")
        ACCESS_URL = os.getenv("ACE_ACCESS_URL")
        EXPORT_TOKEN = os.environ['ACE_EXPORT_TOKEN']

        body = {'ace_export_token': EXPORT_TOKEN}
        headers = {'User-Agent': 'Wget/1.20.1 (linux-gnu)'}
        try:
            response = requests.post(ACCESS_URL, body, headers=headers)
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
        userList = response.json()
        #print("Length of user list: ",len(userList))
        data = response.content
        with open('authorized.json', 'wb') as f:
            f.write(data)
        return userList

    def load_access_list(self):
        """
        Loads the json list of authorized user from file
        """
        #TODO: Currently not used;
        with open('authorized.json', 'r') as json_file :
            authorized_rfids = json.load(json_file)   
            return authorized_rfids

    def postActivityListing(self, credential, authSuccess):
        #print('posting ActivityListing for '+ credential, authSuccess)
        ASSET_ID = os.environ['ACEGC_ASSET_ID']
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        reporting_URL = os.environ['ACEGC_BASE_URL'] + "/activitylistings/"

        data = {
            'access_point': ASSET_ID,
            'activity_date': datetime.now(),
            'credential': credential,
            'success': authSuccess,
        }
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        resp = requests.post(reporting_URL, data, headers=headers)
        #print(resp.content)
        return resp

    def postLaserSession(self,currSession):
        print('posting LaserSession for '+ currSession.credential)
        GC_ASSET_TOKEN = os.environ['ACEGC_ASSET_TOKEN']
        reporting_URL = os.environ['ACEGC_BASE_URL'] + "/lasersessions/"

        data = {
            'credential': currSession.credential,
            'start_time': currSession.start_time,
            'end_time': currSession.end_time,
            'start_odo': currSession.start_odo,
            'end_odo': currSession.end_odo,
        }
        headers = {'Authorization': "Token {}".format(GC_ASSET_TOKEN)}
        resp = requests.post(reporting_URL, data, headers=headers)
        print(resp.content)
