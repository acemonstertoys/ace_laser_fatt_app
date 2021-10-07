import os, sys
import tempfile
import requests

LASERGUI_ROOT = os.environ.get( "LASERGUI_ROOT", "/home/pi/laserGui/" )
AUTHLIST_FILE = "authorized.json"

def fetch_access_list():
    """
    Pulls certified laser RFIDs from URL defined as an environment variable.
    The json list contains only those user allowed to use the laser.
    """
    ACCESS_URL = os.environ['ACE_ACCESS_URL']
    EXPORT_TOKEN = os.environ['ACE_EXPORT_TOKEN']

    body = {'ace_export_token': EXPORT_TOKEN}
    headers = {'User-Agent': 'Wget/1.20.1 (linux-gnu)'}
    try:
        response = requests.post(ACCESS_URL, body, headers=headers)
    except requests.exceptions.Timeout:
        # TODO  Maybe set up for a retry, or continue in a retry loop
        print("Timeout connecting to URL")
        sys.exit(1)
    except requests.exceptions.TooManyRedirects:
        # TODO Tell the user their URL was bad and try a different one
        print("Invalid URL, exiting")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    # print(response.content)
    # print(response.text)

    data = response.content
    authlist = os.path.join( LASERGUI_ROOT, AUTHLIST_FILE )
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(data)
        tf.flush()

        # Atomically replace the old authlist
        os.replace( tf.name, authlist )



if __name__=='__main__':
    fetch_access_list()




