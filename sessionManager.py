from enum import Enum
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
    # Class variables
    auth_URL = os.getenv("LASER_EXPORT_URL")

    def __init__(self, currentUser=None, currentFilter=None):
        # Instance variables
        self.currentUser = currentUser
        self.currentFilter = currentFilter

    def currentFilterData(self):
        #TODO: pull from currentFilter
        return 'Unknown', 0

    def authenticate_credential(self, credential):
        if self.currentUser == None:
            #TODO attempt login
            # fetch accesslist if empty or expired
            # load the accesslist
            # log attmept to GC ActivityListing
            if credential == "005A5891":
                self.currentUser = LaserSession(credential)
                return Auth_Result.AUTHENTICATED
            else: 
                return Auth_Result.NOT_AUTHENTICATED
        elif self.currentUser.credential == credential:
            self.logout(credential)
            return Auth_Result.LOGGED_OUT
        else:
            return Auth_Result.ANOTHER_USER_LOGGED_IN

    def logout(self, credential):
        self.currentUser = None
        #TODO log to GC LaserActivty

    # Untested...
    
    def fetchAccessList(self):
        """Pulls certified laser RFIDs from URL defined as an environment variable"""
        payload = None
        headers = {'User-Agent': 'Wget/1.20.1 (linux-gnu)'}
        # response = requests.get(URL, params=payload, verify=False)
        try:
            response = requests.get(URL, params=payload, headers=headers)
        except requests.exceptions.Timeout:
            #TODO:  Maybe set up for a retry, or continue in a retry loop
            print("Timeout connecting to URL")
            sys.exit(1)
        except requests.exceptions.TooManyRedirects:
            #TODO: Tell the user their URL was bad and try a different one
            print("Invalid URL, exiting")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        rfids = response.content.decode("utf-8").split('\n')
        return rfids

    def cacheRFIDs(self, rfids, filename="authorized.txt"):
        file = open(filename, "w+")
        for token in rfids:
            # short_token = token[-6:]
            short_token = token[-8:]
            file.write(short_token + "\n")

    def load_whitelist(self):
        with open("authorized.txt", 'r') as f:
            authorized_rfids = f.read().split("\n")
            return authorized_rfids
