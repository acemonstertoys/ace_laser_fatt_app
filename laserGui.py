import os
from datetime import datetime, timedelta
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
taggedFob = ""
sessionManager = SessionManager()
last_odo_reading = 0
last_odo_time = datetime.now()

# Functions -----------
def updateTime():
    now = datetime.now()
    format = "%A, %B %d, %Y | %I:%M%p"
    nowStr = now.strftime(format)
    dateTimeText.value = nowStr

def updateFilterData():
    data = sessionManager.currentFilterData()
    filterTypeText.value = data[0]
    filterTimeText.value = str(round(data[1])) + ' Min.'
    if sessionManager.is_filter_change_needed():
        sideBarAlert.visible = True
        sideBar.bg = SIDE_ALERT_COLOR
    else:
        sideBarAlert.visible = False
        sideBar.bg = SIDE_COLOR

def updateLaserOdometer():
    #print("updating odometer")
    global last_odo_reading
    global last_odo_time
    odoReading = sessionManager.update_odometer()
    if odoReading == last_odo_reading: # no activity
        # check length of session inactivity
        LOGOUT_TIME = int(os.environ.get('LASER_LOGOUT_TIME', '40'))
        if datetime.now() > (last_odo_time + timedelta(minutes = LOGOUT_TIME)):
            invokeLogout()
    else: # we have activity
        last_odo_reading = odoReading
        last_odo_time = datetime.now()
        odoBoxOdoText.value = 'ODO: '+ str(odoReading)
        odoBoxCostText.value = 'Session Cost: $'+ sessionManager.currentUser.calculate_session_cost()
        updateFilterData()

def invokeLogout():
    print("invoking logout")
    sessionManager.logout()
    setUpWaiting()

def handleFobTag(event_data):
    #print("handleFobTag()...")
    global taggedFob
    global last_odo_time
    # look for the enter key 
    if ((event_data.tk_event.keycode == 36) or (event_data.tk_event.keysym == "Return")):
        try:
            fobNum = int(taggedFob)
            fobHex = hex(fobNum).upper().lstrip("0X").zfill(8)
            print("Fob = "+ fobHex)
            result = sessionManager.authenticate_credential(fobHex)
        except ValueError as verr:
            print("Invalid Fob Reading: "+taggedFob)
            result = Auth_Result.ERROR
            app.error("Fob Error", "Invalid Fob Reading: "+taggedFob)
        except Exception as ex:
            print("Exception thrown in handleFobTag!")
            result = Auth_Result.ERROR
            app.error("Auth Error", "Error for fob: "+taggedFob)

        if result == Auth_Result.NOT_AUTHENTICATED:
            print("ID: {} Authorized: {}".format(fobHex, False))
            setUpUncertified(fobHex)
        elif result == Auth_Result.AUTHENTICATED:
            print("ID: {} Authorized: {}".format(fobHex, True))
            last_odo_time = datetime.now()
            setUpCertified()
        elif result == Auth_Result.LOGGED_OUT:
            setUpWaiting()
        elif result == Auth_Result.ANOTHER_USER_LOGGED_IN:
            #print("Another user is logged in!!!")
            app.info("Fob Info", "Another user is already logged in")
        # clear out tagged capture 
        taggedFob = ""
    else:
        #print("key = " + event_data.key)
        #print("keycode = " + str(event_data.tk_event.keycode))
        #print("keysym =  " + event_data.tk_event.keysym)
        #print("keysym_num =  " + str(event_data.tk_event.keysym_num))
        taggedFob += event_data.key
        if len(taggedFob) > 10:
            app.warn("Fob Reading Error", "Value read: "+taggedFob)
            taggedFob = ""

def handleNewOrganicsFilter():
    #print("handleNewOrganicsFilter...")
    sessionManager.create_new_filter(FilterType.GREEN_ORGANICS)
    newFilterBox.visible = False
    setUpCertified()

def handleNewSyntheticsFilter():
    #print("handleNewSyntheticsFilter...")
    sessionManager.create_new_filter(FilterType.WHITE_SYNTHETICS)
    newFilterBox.visible = False
    setUpCertified()

def handleChangeFilter(filterObj):
    #print('handleChangeFilter... id='+ filterObj.display_id())
    sessionManager.switch_to_filter(filterObj)
    usedFilterBox.visible = False
    setUpCertified()

def setUpWaiting():
    print("setting up Waiting...")
    app.bg = MAIN_COLOR
    filterStatusBox.bg = FILTER_COLOR
    hideCertified()
    noCertBox.visible = False
    changeFilterBox.visible = False
    newFilterBox.visible = False
    usedFilterBox.visible = False
    welcomeBox.visible = True

def setUpUncertified(userName):
    #print("setting up Uncertified...")
    app.bg = UNAUTH_COLOR
    welcomeBox.visible = False
    noCertBox.visible = True
    app.after(7000, setUpWaiting)

def setUpCertified():
    print("setting up Certified...")
    app.bg = MAIN_COLOR
    updateFilterData()
    userNameText.value =  sessionManager.currentUser.name
    sideBar.visible = True
    welcomeBox.visible = False
    changeFilterBox.visible  = False
    # Schedule call to read odometer based LASER_ODO_POLLING env var
    ODO_INTERVAL = int(os.environ.get('LASER_ODO_POLLING', '15'))
    app.repeat((ODO_INTERVAL * 1000), updateLaserOdometer)
    updateLaserOdometer()
    odoBox.visible = True

def hideCertified():
    #print("hiding Certified...")
    app.cancel(updateLaserOdometer)
    sideBar.visible = False
    odoBox.visible = False

def setUpChangeFilter():
    #print("setting up Change Filter...")
    hideCertified()
    app.bg = CHANGE_FILTER_COLOR
    changeFilterBox.visible  = True

def setUpNewFilter():
    #print("setting up New Filter...")
    changeFilterBox.visible = False
    newFilterBox.visible = True

def setUpExistingFilter():
    #print("setting up Existing Filter...")
    changeFilterBox.visible = False
    usedFilterBox.visible = True
    # tear down filter buttons
    for widget in reversed(usedFilterBtns.children):
        widget.destroy()
    # populate buttons representing list of existing filters
    filters = sessionManager.fetch_existing_filters()
    if len(filters)==0:
        # no existing filters, add a button to create a new filter
        PushButton(usedFilterBtns, command=setUpNewFilter, text="Create New Filter", width=25, pady=15).text_size = 18
    else:
        for lsrFilter in filters:
            PushButton(usedFilterBtns, args = [lsrFilter], command=handleChangeFilter, text=lsrFilter.display_summary(), width=25, pady=15).text_size = 18

# App --------------
app = App(title="laser", width=800, height=480, bg=MAIN_COLOR)
app.font="DejaVu Serif"
app.text_color="white"
app.set_full_screen()   # ESC will exit full screen
app.when_key_pressed = handleFobTag

# Operator Information: side bar
sideBar = Box(app, width=290, height="fill", align="right", visible=False) #, border=True)
opInfoGrid = Box(sideBar, layout="grid", width="fill")
Text(opInfoGrid, text="Operator Information", size=16, color="black", grid=[0,0], align="left")
userNameText = Text(opInfoGrid, text="[Name]", size=16, color="black", grid=[0,1], align="left")
Box(sideBar, width="fill", height=45) # spacer
sideBarAlert = Box(sideBar, width="fill", visible=False)
# GIF and PNG are supported, except macOS which only supports GIF
Picture(sideBarAlert, image="/home/pi/laserGui/images/alert.gif")
Text(sideBarAlert, text="Change Filter!", size=24, color="yellow")
Box(sideBar, width="fill", height=45, align="bottom") # spacer
cfButton = PushButton(sideBar, command=setUpChangeFilter, text="Change Filter", padx=30, align="bottom")
cfButton.text_size = 18
#cfButton.bg = "white" # Not Working
#cfButton.text_color = "black"

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
Text(noCertBox, text="Hello Member", size=48)
Text(noCertBox, text="You do not have a laser certification", size=18)
Text(noCertBox, text="on file and are not authorized to use this laser", size=18)

# CERTIFIED State
odoBox = Box(app, layout="grid", width="fill", align="top", visible=False)
odoBox.text_size=36
Box(odoBox, grid=[0,0], width="fill", height=48) # spacer
odoBoxOdoText = Text(odoBox, text="ODO: 13148709183", grid=[0,1], align="left")
odoBoxCostText = Text(odoBox, text="Session Cost: $1.76", grid=[0,2], align="left", size=30)

# Change Filter
changeFilterBox = Box(app, align="top", width="fill", visible=False) #, border=True)
Box(changeFilterBox, width="fill", height=30) # spacer
changeNoticeBox = Box(changeFilterBox, width="fill") #, border=True)
#changeNoticeBox.bg = "white"
changeNoticeBox.tk.configure(background="white")
changeNoticeBox.text_color = "black"
changeNoticeBox.text_size = 16
#Text(changeNoticeBox, text="Important!", size=18, color=SIDE_ALERT_COLOR)
#Text(changeNoticeBox, text="The filter you are replacing still has life in it.")
#Text(changeNoticeBox, text="Please mark the filter as #F007 when you put it on the shelf.")
#Box(changeFilterBox, width="fill", height=15) # spacer
Text(changeFilterBox, text="What kind of filter are you putting in?", size=16)
Box(changeFilterBox, width="fill", height=15) # spacer
PushButton(changeFilterBox, command=setUpNewFilter, text="New Filter", width=25, pady=15).text_size = 18
Box(changeFilterBox, width="fill", height=15) # spacer
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
Box(usedFilterBox, width="fill", height=15) # spacer
usedFilterBtns = Box(usedFilterBox, width="fill", height="fill")

print("App ready to display...")
app.display()
#app.focus()
