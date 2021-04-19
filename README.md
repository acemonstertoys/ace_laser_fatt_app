# New Laser Odometer
*Graphical User Interace to the makerspace's laser.*
* images — images used in the GUI
* systemd — Systemd service used to automatically start the GUI
* filter.py — represents laser filters
* laser.py — Interface to the Teensy controller *(link TBD)*
* laserGui.py — GUI built on [guizero](https://lawsie.github.io/guizero/) which wraps standard Python Tkinter GUI library.
* laserSession.py — represents a user's session at the laser.
* requirements.txt — python library dependencies
* sessionManager.py — manages interactions between the GUI and users and filters

## Installation
Clone this repo into a directory named *laserGui* in the pi user's home directory. This path is referenced in the service that starts the app. More detail instructions cam be found in [INSTALL.md](./INSTALL.md). Please Note: Environment variables are required. They are not stored in this repo as they are considered sensitive information.
