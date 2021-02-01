from datetime import datetime
from enum import Enum
from filter import Filter, FilterType
from guizero import App, Box, Picture, PushButton, Text
from sessionManager import Auth_Result, SessionManager

# Contant Color Values
MAIN_COLOR = "#3636B2"
FILTER_COLOR = "#222270"
UNAUTH_COLOR = "#8F009B"
UNAUTH_FILTER_COLOR = "#5B2262"
SIDE_COLOR = "#63BBE8"
SIDE_ALERT_COLOR = "#E5008A"
CHANGE_FILTER_COLOR = "#90CFEE"

# Global Variables ----
class UIStates(Enum):
    WAITING = 0
    UNCERTIFIED = 1
    CERTIFIED = 2
    CHANGE_FILTER =3

taggedFob = ""
currentUIstate = UIStates.WAITING
sessionManager = SessionManager()

# Functions -----------
def updateTime():
    now = datetime.now()
    format = "%A, %B %d, %Y | %I:%M%p"
    nowStr = now.strftime(format)
    dateTimeText.value = nowStr

def updateFilterData():
    data = sessionManager.currentFilterData()
    filterTypeText.value = data[0]
    filterTimeText.value = str(data[1]) + ' Min.'

def handleFobTag(event_data):
    #print("handleFobTag()...")
    global taggedFob
    global currentLoginUser
    # look for the enter key 
    if ((event_data.tk_event.keycode == 36) or (event_data.tk_event.keysym == "Return")):
        fobNum = int(taggedFob)
        fobHex = hex(fobNum).upper().lstrip("0X").zfill(8)
        print("Fob = "+ fobHex)

        result = sessionManager.authenticate_credential(fobHex)
        #result = Auth_Result.AUTHENTICATED
        if result == Auth_Result.NOT_AUTHENTICATED:
            print("ID: {} Authorized: {}".format(fobHex, False))
            setUpUncertified(fobHex)
        elif result == Auth_Result.AUTHENTICATED:
            print("ID: {} Authorized: {}".format(fobHex, True))
            setUpCertified()
        elif result == Auth_Result.LOGGED_OUT:
            setUpWaiting()
        elif result == Auth_Result.ANOTHER_USER_LOGGED_IN:
            print("Another user is logged in!!!")
            app.info("Fob Info", "Another user is already logged in")
        else:
            print("Some sort of error!!!")
            app.warn("Fob Info", "Some sort of error!!!")
        # clear out tagged capture 
        taggedFob = ""
    else:
        #print("key = " + event_data.key)
        #print("keycode = " + str(event_data.tk_event.keycode))
        #print("keysym =  " + event_data.tk_event.keysym)
        #print("keysym_num =  " + str(event_data.tk_event.keysym_num))
        taggedFob += event_data.key

def handleNewOrganicsFilter():
    print("handleNewOrganicsFilter...")
    sessionManager.createNewFilter(FilterType.GREEN_ORGANICS)
    newFilterBox.visible = False
    setUpCertified()

def handleNewSyntheticsFilter():
    print("handleNewSyntheticsFilter...")
    sessionManager.createNewFilter(FilterType.WHITE_SYNTHETICS)
    newFilterBox.visible = False
    setUpCertified()

def setUpWaiting():
    print("setting up Waiting...")
    app.bg = MAIN_COLOR
    filterStatusBox.bg = FILTER_COLOR
    sideBar.visible = False
    odoBox.visible = False
    noCertBox.visible = False
    welcomeBox.visible = True

def setUpUncertified(userName):
    print("setting up Uncertified...")
    currentUIstate = UIStates.UNCERTIFIED
    app.bg = UNAUTH_COLOR
    welcomeBox.visible = False
    noCertBox.visible = True
    app.after(7000, setUpWaiting)

def setUpCertified():
    print("setting up Certified...")
    currentUIstate = UIStates.CERTIFIED
    updateFilterData()
    if sessionManager.isFilterChangeNeeded():
        aideBarAlert.visible = True
        sideBar.bg = SIDE_ALERT_COLOR
    else:
        aideBarAlert.visible = False
        sideBar.bg = SIDE_COLOR
    sideBar.visible = True
    welcomeBox.visible = False
    changeFilterBox.visible  = False
    odoBox.visible = True

def setUpChangeFilter():
    print("setting up Change Filter...")
    currentUIstate = UIStates.CHANGE_FILTER
    app.bg = CHANGE_FILTER_COLOR
    sideBar.visible = False
    odoBox.visible = False
    changeFilterBox.visible  = True

def setUpNewFilter():
    print("setting up New Filter...")
    changeFilterBox.visible = False
    newFilterBox.visible = True

def setUpExistingFilter():
    print("setting up Existing Filter...")
    changeFilterBox.visible = False
    usedFilterBox.visible = True

# App --------------
app = App(title="laser", width=800, height=480, bg=MAIN_COLOR)
app.font="DejaVu Serif"
app.text_color="white"
app.when_key_pressed = handleFobTag

# Operator Information: side bar
sideBar = Box(app, width=290, height="fill", align="right", visible=False) #, border=True)
opInfoGrid = Box(sideBar, layout="grid", width="fill")
Text(opInfoGrid, text="Operator Information", size=16, color="black", grid=[0,0], align="left")
Text(opInfoGrid, text="[Name]", size=16, color="black", grid=[0,1], align="left")
Box(sideBar, width="fill", height=45) # spacer
aideBarAlert = Box(sideBar, width="fill", visible=False)
# GIF and PNG are supported, except macOS which only supports GIF
Picture(aideBarAlert, image="./images/alert.gif")
Text(aideBarAlert, text="Change Filter!", size=30, color="yellow")
Box(sideBar, width="fill", height=45, align="bottom") # spacer
PushButton(sideBar, command=setUpChangeFilter, text="Change Filter", padx=30, align="bottom").text_size = 18
#button.bg = "white" # Not Working
#button.text_color = "black"

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
filterTypeText = Text(filterStatusBox, text="", grid=[1,1])
Text(filterStatusBox, text="Filter Time Left: ", grid=[0,2], align="left")
filterTimeText = Text(filterStatusBox, text="", grid=[1,2], align="left")
updateFilterData()

# Welcome Box for the WAITING state
welcomeBox = Box(app, align="top", width="fill")
Box(welcomeBox, width="fill", height=60) # spacer
Text(welcomeBox, text="Welcome", size=72)
Text(welcomeBox, text="Tap your fob to begin", size=36)

# UNCERTIFIED State
noCertBox = Box(app, align="top", width="fill", visible=False)
noCertBox.bg = UNAUTH_COLOR
Box(noCertBox, width="fill", height=60) # spacer
Text(noCertBox, text="Hello [Name]", size=48)
Text(noCertBox, text="You do not have a laser certification", size=18)
Text(noCertBox, text="on file and are not authorized to use this laser", size=18)

# CERTIFIED State
odoBox = Box(app, layout="grid", width="fill", align="top", visible=False)
odoBox.text_size=48
Box(odoBox, grid=[0,0], width="fill", height=48) # spacer
Text(odoBox, text="ODO: 13148709183", grid=[0,1], align="left")
Text(odoBox, text="Session Cost: $1.76", grid=[0,2], align="left")

# Change Filter
changeFilterBox = Box(app, align="top", width="fill", visible=False) #, border=True)
Box(changeFilterBox, width="fill", height=60) # spacer
changeNoticeBox = Box(changeFilterBox, width="fill") #, border=True)
#changeNoticeBox.bg = "white"
changeNoticeBox.tk.configure(background="white")
changeNoticeBox.text_color = "black"
changeNoticeBox.text_size = 16
Text(changeNoticeBox, text="Important!", size=18, color=SIDE_ALERT_COLOR)
Text(changeNoticeBox, text="The filter you are replacing still has life in it.")
Text(changeNoticeBox, text="Please mark the filter as #F007 when you put it on the shelf.")
Box(changeFilterBox, width="fill", height=30) # spacer
Text(changeFilterBox, text="What kind of filter are you putting in?", size=16)
Box(changeFilterBox, width="fill", height=15) # spacer
PushButton(changeFilterBox, command=setUpNewFilter, text="New Filter", width=25, pady=15).text_size = 18
Box(changeFilterBox, width="fill", height=10) # spacer
PushButton(changeFilterBox, command=setUpExistingFilter, text="Used Filter", width=25, pady=15).text_size = 18

# New Filter
newFilterBox = Box(app, align="top", width="fill", visible=False)
Box(newFilterBox, width="fill", height=60) # spacer
Text(newFilterBox, text="What kind of filter are you putting in?", size=16)
Box(newFilterBox, width="fill", height=30) # spacer
PushButton(newFilterBox, command=handleNewOrganicsFilter, text="Green Filter for organics", width=25, pady=15).text_size = 18
Box(newFilterBox, width="fill", height=15) # spacer
PushButton(newFilterBox, command=handleNewSyntheticsFilter, text="White Filter for synthetics", width=25, pady=15).text_size = 18

# Existing Filter
usedFilterBox = Box(app, align="top", width="fill", visible=False)
Box(usedFilterBox, width="fill", height=60) # spacer
Text(usedFilterBox, text="Which used filter are you putting in?", size=16)

print("App ready to display...")
app.display()
app.focus()