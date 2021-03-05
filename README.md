# New Laser Odometer
*TBD description*
* images — 
* laser.py — Interface to the Teensy controller *(link TBD)*
* laserGui.py — GUI built on [guizero](https://lawsie.github.io/guizero/) which wraps standard Python Tkinter GUI library.
* laserSession.py — 
* requirements.txt — python library dependencies
* sessionManager.py — 

## Development Environment
*TBD overview description*
1. Create a virtual environment: ```python3 -m venv env```
2. Install dependencies via requirements.txt: ```pip install -r requirements.txt```

## Deployment
*TBD overview description*
1. Update the Pi:
```
sudo apt-get update
sudo apt-get upgrade
```
1. *TDB: get the souce on to the device*
2. make sure the startup script is executable: ```chmod 755 kiosk.sh```
3. set environment variables

## Environment Variables
*TBD overview description*
* ACE_ACCESS_URL — the access list URL
* ACE_EXPORT_TOKEN - 
* ACEGC_ASSET_ID —
* ACEGC_ASSET_TOKEN — 
* ACEGC_BASE_URL - base URL to Grand Central
* ACEGC_LASER_COST — the cost in cents per minute of laser firing. Default is 0.5
* ACEGC_LOGOUT_TIME - Default is 40.
