from datetime import datetime
from enum import Enum
from getrfids import *
from guizero import App, Box, Text, PushButton
from laser import *

# Contant Color Values
MAIN_COLOR = "#3636B2"
FILTER_COLOR = "#222270"
UNAUTH_COLOR = "#8F009B"
UNAUTH_FILTER_COLOR = "#5B2262"
SIDE_COLOR = "#64BAE7"
SIDE_ALERT_COLOR = "#E5008A"
CHANGE_FILTER_COLOR = "#64BAE7"

# Global Variables ----
class UIStates(Enum):
    WAITING = 0
    UNCERTIFIED = 1
    CERTIFIED = 2
    CHANGE_FILTER =3

taggedFob = ""
currentUIstate = UIStates.WAITING 
currentLoginUser = ""

# Functions -----------
def updateTime():
    now = datetime.now()
    format = "%A, %B %d, %Y | %I:%M%p"
    nowStr = now.strftime(format)
    dateTimeText.value = nowStr

def handleFobTag(event_data):
    #print("handleFobTag()...")
    global taggedFob
    global currentLoginUser
    # look for the enter key 
    if ((event_data.tk_event.keycode == 36) or (event_data.tk_event.keysym == "Return")):
        fobNum = int(taggedFob)
        fobHex = hex(fobNum).upper().lstrip("0X").zfill(8)
        print("Fob = "+ fobHex)
        
        if fobHex == currentLoginUser:
            #log out existing user
            currentLoginUser = ""
            setUpWaiting()
        elif fobHex in authorized_rfids:
            #log in certified user
            print("ID: {} Authorized: {}".format(fobHex, True))
            currentLoginUser = fobHex
            setUpCertified(fobHex)
        else:
            #log uncertified user
            print("ID: {} Authorized: {}".format(fobHex, False))
            setUpUncertified(fobHex)
        # clear out tagged capture 
        taggedFob = ""
    else:
        #print("key = " + event_data.key)
        #print("keycode = " + str(event_data.tk_event.keycode))
        #print("keysym =  " + event_data.tk_event.keysym)
        #print("keysym_num =  " + str(event_data.tk_event.keysym_num))
        taggedFob += event_data.key
    
def handleButton():
    print("Button was pressed")
    setUpChangeFilter()

def setUpWaiting():
    print("setting up Waiting...")
    app.bg = MAIN_COLOR
    filterStatusBox.bg = FILTER_COLOR
    feesBox.visible = False
    odoBox.visible = False
    noCertBox.visible = False
    welcomeBox.visible = True

def setUpUncertified(userName):
    print("setting up Uncertified...")
    currentUIstate = UIStates.UNCERTIFIED
    app.bg = UNAUTH_COLOR
    filterStatusBox.bg = UNAUTH_FILTER_COLOR
    welcomeBox.visible = False
    noCertBox.visible = True
    app.after(7000, setUpWaiting)

def setUpCertified(userName):
    print("setting up Certified...")
    currentUIstate = UIStates.CERTIFIED
    feesBox.visible = True
    app.bg = MAIN_COLOR
    welcomeBox.visible = False
    odoBox.visible = True

def setUpChangeFilter():
    print("setting up Change Filter...")
    currentUIstate = UIStates.CHANGE_FILTER
    welcomeBox.visible = False
    
# App --------------
app = App(title="laser", width=800, height=480, bg=MAIN_COLOR)
app.font="DejaVu Serif"
app.text_color="white"
app.when_key_pressed = handleFobTag

# Additional Set Up
authorized_rfids = load_whitelist()

# Operator Information: side bar
feesBox = Box(app, width=290, height="fill", align="right", visible=False)
feesBox.bg = SIDE_COLOR
feesBox.text_size=16
Text(feesBox, text="Operator Information")
Text(feesBox, text= "February Fees: $4.56")
Box(feesBox, width="fill", height=45, align="bottom") # spacer
button = PushButton(feesBox, command=handleButton, text="Change Filter", padx=30, align="bottom")
#button.bg = "white" # Not Working
#button.text_color = "black"
button.text_size = 18

# Date & Time: always visible
dateTimeBox = Box(app, width="fill", align="top")
dateTimeText = Text(dateTimeBox, text="Monday, February 6, 2000 | 8:00pm", size=16, align="left")
dateTimeText.repeat(60000, updateTime) # Schedule call to update time very minute
updateTime()

# Filter Status: always visible
filterStatusBox = Box(app, layout="grid", width="fill", height=130, align="bottom") #, border=True)
filterStatusBox.bg = FILTER_COLOR
filterStatusBox.text_size=24
Box(filterStatusBox, grid=[0,0], width="fill", height=20) # spacer
Text(filterStatusBox, text="Current Filter:", grid=[0,1], align="left")
currentFilter = Text(filterStatusBox, text="Organics", grid=[1,1])
Text(filterStatusBox, text="Filter Time Left: ", grid=[0,2], align="left")
filterTime = Text(filterStatusBox, text="83 Min.", grid=[1,2], align="left")

# Welcome Box for the WAITING state
welcomeBox = Box(app, align="top", width="fill")
Box(welcomeBox, width="fill", height=60) # spacer
Text(welcomeBox, text="Welcome", size=72)
Text(welcomeBox, text="Tap your fob to begin", size=36)

# UNCERTIFIED State
noCertBox = Box(app, align="top", width="fill", visible=False)
Box(noCertBox, width="fill", height=60) # spacer
Text(noCertBox, text="Hello [Name]", size=48)
Text(noCertBox, text="You do not have a laser certification", size=18)
Text(noCertBox, text="on file and are not authorized to use this laser", size=18)

# CERTIFIED State
odoBox = Box(app, align="top", width="fill", visible=False)
odoBox.text_size=24
Box(odoBox, width="fill", height=30) # spacer
Text(odoBox, text="Welcome [Name]")
Text(odoBox, text="ODO: 13148709183")
Text(odoBox, text="Session Cost: $1.76")

print("App ready to display...")
app.display()
app.focus()