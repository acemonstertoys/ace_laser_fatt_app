# Installation
This document goes over preparing the Raspberry Pi, acquiring the app, configuring the app, as well as starting and stopping the app through the systemd service.

1. Update the Pi:
```
$ sudo apt-get update
$ sudo apt-get upgrade
```
2. The laser GUI app is a python built on [guizero](https://lawsie.github.io/guizero/), and as such it has a number of dependencies. Install dependencies using requirements.txt: ```pip install -r requirements.txt```
3. Clone this repo: ```$ git clone https://github.com/acemonstertoys/fatt_device```
4. Create a ```prod.env``` file to define the following enviroment vaiables:

| Key | Description | Default Value |
| --- | ----------- | ------------- |
| ACE_ACCESS_URL | the access list URL | none, required |
| ACE_EXPORT_TOKEN | used with ACE_ACCESS_URL | none, required |
| ACEGC_ASSET_ID | the Assest ID of the pi | none, required |
| ACEGC_ASSET_TOKEN | auth token | none, required |
| ACEGC_BASE_URL | base URL to Grand Central | none, required |
| ACEGC_LASER_COST | the cost in cents per minute of laser firing | 0.5 |
| LASER_LOGOUT_TIME | number of inactivity minutes which invokes a logout | 40 |
| LASER_ODO_POLLING | the time interval used to continously poll the laser for odometer reading, in seconds | 15 |

5. Link systemd file from this repo to ```/etc/systemd/system```
```
$ sudo ln -s /home/pi/laserGui/systemd/kiosk.service /etc/systemd/system/kiosk.service
```
6. Load service into systemd: \
`sudo systemctl daemon-reload`
7. Enable the service to start on restart: \
`sudo systemctl enable kiosk.service`
8. Start the service immediately: \
`sudo systemctl start kiosk.service`
9. If needed, stop the service temporarily: \
`sudo systemctl stop kiosk.service`
10. If needed, disable the service until it's enabled again: \
`sudo systemctl disable kiosk.service`
