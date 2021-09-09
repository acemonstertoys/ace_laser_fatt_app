# ace_laser_fatt_app

----
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p float="left" align="center">
<img src="assets/20210711_083104.jpg" width="48%"> 
<img src="assets/20210414_185104.jpg" width="48%">
</p>

<h2 align="left">Ace_laser_FATT_app is a laser cutter access control system</h2>


<!-- <h4 align="center">________________________</h4> -->

# Summary
This repository contains the code we are currently using to track laser usage for our membership, while this is still in the early stages with more features and better stability planned, it is fully usable and includes the following features:
- Gate user access based on credentials associated with their account (using a USB RFID reader and crosschecking against an access list)
- Activate and deactivate the Laser for cutting (using a teensy connected to the Laser Cutter)
- Periocally get an update for Laser usage (the Laser reports an odometer - in seconds - which we store on the teensy and check for updates)
- Track a user session to gather the amount of firing time the member used (this is uploaded to our database from which we generate invoices through a custom Wordpress plugin)
- Allow users to select which filter they are using
- Track filter usage against firing time and upload to our database for persistence
- Warn users when a filter requires changing

This project and its documentation are recommended for parties with intermediate-advanced technical knowledge due to its unfinished state, if you wish to implement it for your own makerspace / hackerspace we incourage you to make sure you are comfortable with Raspberry Pis, Linux, programmable microcontrollers, Python, basic electronics and have the ability to make your own APIs.
We hope to be able to provide better documentation, install procedures and open source our API endpoints and Wordpress plugin in the future along side the stability improvements and additional features.


# Contents
### - *[Project Overview](#project-overview)*
### -  *[Project Photos](#project-photos)*
### -  *[Quick Start](#quick-start)*
### -  *[Installation](#installation)*
### -  *[For Developers](#for-developers)*
### -  *[Contributors](#contributors)*
### -  *[API](#api)*
### -  *[License](#license)*


---
# Project Overview
### Ace laser FATT (Fob All The Things) app is a laser cutter access control system that allows Ace Makerspace to charge for laser cutting time and track filter usage. It enables users to log laser usage time, using RFID keys to authenticate which user is actively logged in.
 

### The hardware used is a Raspberry Pi, a touch screen, an RFID reader, and a custom-built electronic laser cutter interface built upon a teensy microcontroller.

-----------------
# Project Photos
- <img src="assets/20210414_180447.jpg" width="400"> 
- <img src="assets/20210414_185104.jpg" width="400"> 
- <img src="assets/20210414_185201.jpg" width="400"> 
- <img src="assets/20210414_185207.jpg" width="400"> 
- <img src="assets/20210711_083104.jpg" width="400"> 
- <img src="assets/20210711_083122.jpg" width="400"> 
- <img src="assets/20210711_083131.jpg" width="400"> 
- <img src="assets/20210711_083243.jpg" width="400"> 
- <img src="assets/20210711_083311.jpg" width="400"> 
 

# Quick Start
### for all the commands in one block

##### for more details about the commands see *[Installation](#Installation)*
```bash
sudo apt-get update
sudo apt-get upgrade
cd ~
git clone https://github.com/acemonstertoys/ace_laser_fatt_app
cd ./ace_laser_fatt_app
pip install -r requirements.txt
touch prod.env
nano prod.env # add env variables here
sudo ln -s /home/pi/laserGui/systemd/kiosk.service /etc/systemd/system/kiosk.service
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service
# to stop run 
sudo systemctl stop kiosk.service
# to stop disable 
sudo systemctl disable kiosk.service
``` 




---
# Installation

Bellow is instructions for preparing the Raspberry Pi, acquiring the app, configuring the app, as well as starting and stopping the app through the systemd service.

### 1. Update the Pi:
```bash
sudo apt-get update
sudo apt-get upgrade
```
### 2. Clone this repo: 
#### Clone this repo into a directory named *laserGui* in the pi user's home directory. This path is referenced in the service that starts the app.
```bash
cd ~
git clone https://github.com/acemonstertoys/ace_laser_fatt_app
cd ./ace_laser_fatt_app
```
### 3. Install dependencies using requirements.txt: 
##### The laser GUI app is a python built on [guizero](https://lawsie.github.io/guizero/), and as such it has a number of dependencies. 
```bash
pip install -r requirements.txt
```
### 4. Create a ```prod.env``` file to define the following enviroment vaiables:
#### Note: They are not stored in this repo as they are considered sensitive information.

| Key               | Description                                                                           | Default Value  |
| ----------------- | ------------------------------------------------------------------------------------- | -------------- |
| ACE_ACCESS_URL    | the access list URL                                                                   | none, required |
| ACE_EXPORT_TOKEN  | used with ACE_ACCESS_URL                                                              | none, required |
| ACEGC_ASSET_ID    | the Assest ID of the pi                                                               | none, required |
| ACEGC_ASSET_TOKEN | auth token                                                                            | none, required |
| ACEGC_BASE_URL    | base URL to Grand Central                                                             | none, required |
| ACEGC_LASER_COST  | the cost in cents per minute of laser firing                                          | 0.5            |
| LASER_LOGOUT_TIME | number of inactivity minutes which invokes a logout                                   | 40             |
| LASER_ODO_POLLING | the time interval used to continously poll the laser for odometer reading, in seconds | 15             |

#### Example `prod.env` file:
```toml
# [prod.env]
ACE_ACCESS_URL=
ACE_EXPORT_TOKEN=
ACEGC_ASSET_ID=
ACEGC_BASE_URL=
ACEGC_LASER_COST=
LASER_LOGOUT_TIME=
LASER_ODO_POLLING=
```

### 5. Link systemd file from this repo to ```/etc/systemd/system```
```
sudo ln -s /home/pi/laserGui/systemd/kiosk.service /etc/systemd/system/kiosk.service
```
### 6. Load service into systemd: 
```bash
sudo systemctl daemon-reload
```
### 7. Enable the service to start on restart: 
```bash
sudo systemctl enable kiosk.service
```
### 8. Start the service immediately: 
#### Please Note: Environment variables are required.
```bash
sudo systemctl start kiosk.service
```
### 9. If needed, stop the service temporarily: 
```bash
sudo systemctl stop kiosk.service
```
### 10. If needed, disable the service until it's enabled again:
```bash
sudo systemctl disable kiosk.service
```

----

# API
## Data type info

### Session Manager Data Types
| Name | Datatype | value |
| --- | --- | --- |
| credential   | String ( hex )| see userDict['RFID'] | 
| authSuccess  | Boolean |   True/False | 
| member_id    | String |  see userDict['UID'] | 
| start_time   | String |  UTC String EX'2021-07-24 16:03:43.415006' | 
| end_time     | String |  UTC String EX'2021-07-24 16:03:43.415006' (python datetime.now()) | 
| start_odo    | long (seconds) |  Ex 0 | 
| end_odo      | long (seconds) |  EX: 0 laser.py laserInterface.odometer  | 
| CURRENT_TIME | String |  UTC String EX'2021-07-24 16:03:43.415006' | 


### Filter Data Types
| Name | Datatype | value |
| --- | --- | --- |
| filterId         | long |  |
| filterType       | Enum FilterType |  |
| --> GREEN_ORGANICS   | long (minutes) |  Green organics filters can be used for a total of 140 minutes  |
| --> WHITE_SYNTHETICS | long (minutes) |  White synthetics filter can be used for a total of 60 minutes  |
| --> Unknown          | long (minutes) |  Unknown filter type |
| recordedUsage    | long |  |
| odometerReading  | long (seconds) |  |

----

# SessionManager
## fetch_access_list
### POST /<ACE_ACCESS_URL>/
<!-- ### Description: fetch_access_list       -->
```
Pulls certified laser RFIDs from URL defined as an environment variable.
The json list contains only those user allowed to use the laser.
```
##### Request Example:
```json
{
    "headers":
    {
        "User-Agent": "Wget/1.20.1 (linux-gnu)"
    },
    "body":
    {
        "ace_export_token": <ACE_EXPORT_TOKEN>
    }
}
```
##### Response Example:
```json

// <LIST> returns the current list of users allowed to use the laser.
[
    {
        "RFID": <STRING>,
        "First Name": <STRING>,
        "Last Initial": <STRING upper case length 1> , 
        "UID": <int>
    },
    {...}
    ,
    ....
]

```
| Code | Description |
| ---- | ----------------- |
| 200  | OK                |

## postActivityListing
### POST /<ACE_ACCESS_URL>/activitylistings/
<!-- ### Description:        -->
##### Request Example:
```json
{
    "headers":
    {
        "Authorization": "Token <ACEGC_ASSET_TOKEN>",
    },
    "body":
    {
            "access_point": <ACEGC_ASSET_ID> ,
            "activity_date": <CURRENT_TIME (utc)>,
            "credential": <credential>,
            "success": <authSuccess>,
        }
}
```
##### Response Example:

| Code | Description |
| ---- | ----------------- |
| 200  | OK                |

## postLaserSession
### POST /<ACE_ACCESS_URL>/lasersessions/
### Description: postLaserSession      
##### Request Example:
```json
{
    "headers":
    {
        "Authorization": "Token <ACEGC_ASSET_TOKEN>",
    },
    "body":
    {
            "credential": <credential>,
            "member_id": <member_id>,
            "start_time": <start_time>,
            "end_time": <end_time>,
            "start_odo": <start_odo>,
            "end_odo": <end_odo>,
    }
}
```
##### Response Example:

| Code | Description |
| ---- | ----------------- |
| 200  | OK                |
------

# Filter Api calls
## create_new_filter
### POST `/<ACEGC_BASE_URL>/filters/`
```
Creates a new filter in Grand Central
```
##### Request Example:
```json
{
"header": {
    'Authorization': "Token <ACEGC_ASSET_TOKEN>",
    "Content-Type": "application/json"
},
"body": {
    'seconds_used': 0,
    'seconds_used': <totalUsage>,
    'filter_type': <filterType>,

}
```
##### Response Example:

| Code | Description |
| ---- | ----------------- |
| 200  | OK                |

----

## fetch_existing_filters
### GET `/<ACEGC_BASE_URL>/filters/`
```
Fetch existing filters from GC
```
##### Request Example:
```python
header = {
    "Authorization": "Token <ACEGC_ASSET_TOKEN>",
    "Content-Type": "application/json"
}
requests.get("<ACEGC_BASE_URL>/filters/", headers=header)
```
##### Response Example:

```json
{
    "body": {
        [ //list of filters
            {
                "filter_type": <filterType "O": "GREEN_ORGANICS","S":"WHITE_SYNTHETICS">,
            },
            ...
        ]
    }
}

```

| Code | Description |
| ---- | ----------------- |
| 200  | OK                |
----

## updateRuntime
### PATCH `/<ACEGC_BASE_URL>/filters/<filterId>/`
##### updateRuntime: Calculates usage and posts it to Grand central
##### Request Example:
```json
{
    "header": {
        "Authorization": "Token <ACEGC_ASSET_TOKEN>",
    },
    "body": {
        "seconds_used": <totalUsage>,
    }
}
```

##### Response Example:

| Code | Description |
| ---- | ----------------- |
| 200  | OK                |
----
<!-- Options -->
<!-- payload -->
<!-- Sagger api stuff -->

# Hardware
### NOTE: the hardware is intended for experienced electrical engineers only. Your expected to build your own hardware interface with the laser you are using. We are only showing an example of how we've done ours.
### Teensy Interface
#### The interface is documented here: https://github.com/acemonstertoys/laser-rfid
### Bom
| Item | Quantity |
| ---- | ----------------- |
| USB cable | 1 |
| Raspberry Pi 3 | 1 |
| Teensy 2.0 24 pin version | 1 |
| Touch Screen (Raspberry Pi compatible) | 1 |
| RFID Reader (USB) | 1 |
| BC550 | 1 | 

### Circuit
- <img src="assets\circuit_board_topside.jpg" width="400"> 
- <img src="assets\circuit_board_bottom.jpg" width="400"> 
- <img src="assets\circuit_board_transistor_backside.jpg" width="400"> 
- <img src="assets\circuit_board_transistor.jpg" width="400">
### Schematic
- <img src="assets/schematic_diagram.png" width="400"> 
- <img src="assets/2021-07-26-17-16-01.png" width="400"> 
-----------------
# For Developers

### What each file does
*Graphical User Interace to the makerspace's laser.*
* images — images used in the GUI
* systemd — Systemd service used to automatically start the GUI
* filter.py — represents laser filters
* laser.py — Interface to the Teensy controller *(link TBD)*
* laserGui.py — GUI built on [guizero](https://lawsie.github.io/guizero/) which wraps standard Python Tkinter GUI library.
* laserSession.py — represents a user's session at the laser.
* requirements.txt — python library dependencies
* sessionManager.py — manages interactions between the GUI and users and filters


-----------------
# Contributors
[![](https://contrib.rocks/image?repo=acemonstertoys/ace_laser_fatt_app)](https://github.com/acemonstertoys/ace_laser_fatt_app/graphs/contributors)

##### Made with [contributors-img](https://contrib.rocks).

-----------------
# License
#### MIT © Ace Makerspace
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
#### Documentation Contributor [2021]
```bash
by oran collins
github.com/wisehackermonkey
oranbusiness@gmail.com
20210717
```
