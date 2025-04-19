import os
import random
import http
import sys
import copy
import threading
import time 

from http.server import BaseHTTPRequestHandler, HTTPServer

import urllib.parse
 

import helpers_html as html
import helpers_collisiondetection as collisiondetection 
import helpers_filesystem as filesystem 


movementPerformed=False
requestId=0
refreshGUI = False
useThreads=False
threads = []
totalThreads = 0

sys.setrecursionlimit(5000)
branchCounter = 0


mostEfficient = 99999999
mostEfficientRoute = []

autoPilotDistance=0
autoPilotStepLimit=3 # this ensures that inneficient routes are not considered.

maxApDeviation=0
#If the steps are more than 2x the distance, drop the branch

goodPathsLimit=3
currentGoodPaths=0
currentBadPaths=0

level2ApPathsList=[]

aplevel2PathedCoordinates=[]

#this determines how the world will be rendered to the browser	
perspectiveX="right"    #left or right
perspectiveY="top"  #top or bottom


blocksize = 10 #how many pixels wide and tall a block is in the world. a block represents a cubic meter
padtop= 10 # where to start rendering the world on the up/down axis
padleft=50 # where to start rendering the world on the left/right axis

#when rendering to imply height difference, how much shift should occur
perspectiveTopPad = blocksize / 4 # up/down
perspectiveLeftPad = blocksize / 4  #left/right
       
      
defaultFlightHeight = 10 # prefered height that the drone should fly
maxFlightHeight = 15 # max height the drone is allowed to achieve
 

viewPort=None




apPath = []
#apPath.append(spacialObject("appath",0, 0,0))        

theWorld = [] #this array contains the world... literally. it is an array of arrays of arrays (x,y,z) 
knownObjs= [] #this is an array of known objects. this contains the drone, the base, objects found, etc       

longTermGoalAchieved=False # this is the trigger for if the long term goal has been achieved
droneActions="" # this is a variable that stores the actions the drone is taking during this iteration

query_string="" # this holds the query string that is in use for this request 
action = "" # this is the first param passed in url usually. it defines the action that will take place
value1 = ""
value2 = ""
value3 = ""
value4 = ""
value5 = ""
value6 = "" 
world = ""
drone=""
autoPilotDestination = None #this holds the destination (as an object) for autopilot when enabled
base="" 
 
debugStatements=""

class spacialObject(collisiondetection.spacialCoordinate):

    def renderIt(self):
        global perspectiveX, perspectiveY

        retval = ""

        # Render shadows for depth, excluding "ground"
        if self.name != "ground":
            for objectLayer in range(self.z - self.depth, self.z):
                renderLayer = self.z - objectLayer
                top = padtop + (self.x * blocksize) + shiftTopPerspectiveByLayer(objectLayer)
                left = padleft + (self.y * blocksize) + shiftLeftPerspectiveByLayer(objectLayer)

                retval += (
                    f"\n<div title='Shadow-{renderLayer}: {self.getLabel()}' "
                    f"style='top: {int(top)}; left: {int(left)}; z-index: {int(renderLayer)}; "
                    f"width: {int(blocksize) * self.width}px; height: {int(blocksize) * self.height}px;' "
                    "class='shad'></div>\n"
                )

        # Render the actual object
        top = padtop + (self.x * blocksize) + shiftTopPerspectiveByLayer(self.z)
        left = padleft + (self.y * blocksize) + shiftLeftPerspectiveByLayer(self.z)

        # Use sD for AP level 1 (change to sD2 for AP level 2 if needed)
        retval += (
            f"\n<div onclick='sD({self.x}, {self.y}, {self.z + 1})' "
            f"title='Object: {self.getLabel()}' "
            f"style='position: absolute; top: {top}; left: {left}; z-index: {self.z}; "
            f"width: {int(blocksize) * self.width}px; height: {int(blocksize) * self.height}px;' "
            f"class='mo {self.name}'></div>"
        )

        return retval



def removeKnownObjectByName(objName):
    global knownObjs
    for eachObj in knownObjs:
        if (eachObj.name==objName):
            knownObjs.remove(eachObj)
            
def getBranchId():
    global branchCounter
    branchCounter = branchCounter + 1
    return branchCounter

def debug(what):
    global debugStatements
    debugStatements=debugStatements + "<BR>" + what

def shiftTopPerspectiveByLayer(layer):
    
    if (perspectiveY=="top"):
        retval = -(layer * perspectiveTopPad)             
    if (perspectiveY=="bottom"):
        retval = layer * perspectiveTopPad
    return retval

def shiftLeftPerspectiveByLayer(layer):
    
    if (perspectiveX=="right"):            
         retval = layer * perspectiveLeftPad
    if (perspectiveX=="left"):            
         retval= -(layer * perspectiveLeftPad)
    return retval
    
def loadQS():
    global action
    global value1
    global value2
    global value3
    global value4
    global value5
    global value6
    global query_string
    query_params = urllib.parse.parse_qs(query_string)
    action = query_params.get('action',[''])[0]
    value1 = query_params.get('value1',[''])[0]
    value2 = query_params.get('value2',[''])[0]
    value3 = query_params.get('value3',[''])[0]
    value4 = query_params.get('value4',[''])[0]
    value5 = query_params.get('value5',[''])[0]
    value6 = query_params.get('value6',[''])[0]
     

 
def addKnownObject(theObj):
    global knownObjs
    isNewObj=True
    
    for kObj in knownObjs:
        if (kObj.name==theObj.name and kObj.x==theObj.x and kObj.y==theObj.y and kObj.z==theObj.z):
            isNewObj=False
    
    if isNewObj==True:
        theObj.id = len(knownObjs)
        knownObjs.append(theObj)
    #else:
    #    print("Dupe obj: " + theObj.getLabel())
    
  

def createObstacles():
   
    #make some trees
    howManyTrees = random.randint(3, 10)
    for treeLoop in range(howManyTrees):
        thex = random.randint(1, world.x -1)
        they = random.randint(1, world.y -1)
        treeHeightRND = random.randint(5, world.z -1) 
        treeTrunkHeightRND = random.randint(4, treeHeightRND) 
        for thisLevel in range(treeHeightRND):
            treeHeight = treeHeightRND - thisLevel
            # place top of tree
            addKnownObject(spacialObject("tree",thex  ,they ,treeHeightRND))
            #create growing layers until hitting ground
            for thisLayerRange in range(thisLevel -1):
                if (treeHeight < treeTrunkHeightRND):
                    #create trunk
                    addKnownObject(spacialObject("treetrunk",thex ,they ,treeHeight))
                else:
                    #create next layer of leaves
                    addKnownObject(spacialObject("tree",thex + thisLayerRange ,they ,treeHeight))
                    addKnownObject(spacialObject("tree",thex - thisLayerRange ,they ,treeHeight))
                    addKnownObject(spacialObject("tree",thex  ,they + thisLayerRange,treeHeight))
                    addKnownObject(spacialObject("tree",thex  ,they - thisLayerRange,treeHeight))
            
    # make some random walls
    for wallCounter in range(1,random.randint(1,5)):
        rndHeight= random.randint(4, maxFlightHeight) 
        addKnownObject(spacialObject("wall",random.randint(4, 30) ,random.randint(4, 30) ,rndHeight ,random.randint(1, 5) ,random.randint(1, 5) , rndHeight ))    
 
    addKnownObject(spacialObject("wall",7,5,5,15,1,4))
    addKnownObject(spacialObject("wall",17,15,5,15,1,4))
    
    addKnownObject(spacialObject("poi",35,15,1))
    addKnownObject(spacialObject("poi",35,30,1))
    addKnownObject(spacialObject("poi",35,45,1))
    addKnownObject(spacialObject("poi",35,50,1))

    
    addKnownObject(spacialObject("poi",5,15,1))
    addKnownObject(spacialObject("poi",5,30,1))
    addKnownObject(spacialObject("poi",5,45,1))
    addKnownObject(spacialObject("poi",5,50,1))


    addKnownObject(spacialObject("poi",15,2,1))
            
    addKnownObject(spacialObject("poi",15,50,1))

    addKnownObject(spacialObject("wall",4,1,maxFlightHeight ,1,4, maxFlightHeight ))          

#make large walls that cant be flown over
    #for theheight in range(defaultFlightHeight + 5):
    addKnownObject(spacialObject("wall",15,25,maxFlightHeight ,15,1,maxFlightHeight ))     
    addKnownObject(spacialObject("wall",24,5,maxFlightHeight ,1,25, maxFlightHeight ))
    addKnownObject(spacialObject("wall",20,10,maxFlightHeight ,1,25, maxFlightHeight ))          
 
def renderActions(self):
    global longTermGoalAchieved
    global droneActions
    global action
    global value1
    global value2
    global value3
    global value4
    global value5
    global value6
    
    parsed_path = urllib.parse.urlparse(self.path)
    query_string = parsed_path.query
         
    # Parse the query string into a dictionary        
    query_params = urllib.parse.parse_qs(query_string)
        

    
    retval = ""
    if (longTermGoalAchieved==True):
        resetAP()
         
            
            
    retval +=  "\n <BR>Drone actions: " + droneActions.replace("<","<BR>") + "<BR><BR>"
    retval +=  html.makeLink("/?action=move&value=left","<") + " | "  + html.makeLink("/?action=move&value=right",">") + " | "
    retval +=  html.makeLink("/?action=move&value=up","/\\") + " | " + html.makeLink("/?action=move&value=down","\\/") + " | "
    retval +=  html.makeLink("/?action=move&value=higher","Raise") + " | "  + html.makeLink("/?action=move&value=lower","Lower") + " | "
    retval +=  html.makeLink("/?action=randomworld","Randomize World") + " | "
    retval +=  html.makeLink("/?action=perspectiveX&value1=left","perspective left") + " | "
    retval +=  html.makeLink("/?action=perspectiveX&value1=right","perspective right") + " | "
    retval +=  html.makeLink("/?action=perspectiveY&value1=top","perspective top") + " | "
    retval +=  html.makeLink("/?action=perspectiveY&value1=bottom","perspective bottom") + " | "
    retval +=  html.makeLink("/","Refresh") + " | "
    
 
    retval +=  "\n<BR><BR> " + html.makeInput("action","ip")
    retval +=  html.makeInput("value1","ip")  + html.makeInput("value2","ip")
    retval +=  html.makeInput("value3","ip")  + html.makeInput("value4","ip")
    retval +=  html.makeInput("value5","ip") + html.makeInput("value6","ip")
    
    
    retval +=  "\n <input type='button' value='run' onclick='subForm();'>\n "
    return retval

def resetAP():
    global longTermGoalAchieved
    global droneActions
    global autoPilotDestination
    global movementPerformed
    
    movementPerformed=False
    longTermGoalAchieved=False     
    autoPilotDestination=None        
    removeKnownObjectByName("apdestination")

def renderScripts(self):
    retval = "\n <script>  "
    retval +=  "\n window.droneX=" + str(drone.x)
    retval +=  "\n window.droneY=" + str(drone.y)
    retval +=  "\n window.droneZ=" + str(drone.z)
    retval +=  "\n </script>  "
    #retval +=  "\n setTimeout(autoPilot, 2000); \n </script>"
    
    if (autoPilotDestination != None):
#        retval +=  "\n <script> alert('done'); /* setTimeout(autoPilotRefresh, 1000); */ \n </script>"
        #if refreshGUI == True:
        retval +=  "\n <script>   setTimeout(autoPilotRefresh, 1000);   \n </script>"
        #else:
        #    retval += "Not refreshing gui"
    return retval

def renderWorld(self):
    #let timeoutId = setTimeout(greet, 2000, "World")
    response_content = "<BR>" + drone.getLabel() + "<BR> World: " + world.getLabel()
    response_content +=  "  <BR> Known objects: " + str(len(knownObjs))
    
    response_content +=  "  <BR> defaultFlightHeight: " + str(defaultFlightHeight)
    response_content +=  "  <BR> maxFlightHeight: " + str(maxFlightHeight)
    
     
    if (autoPilotDestination!=None):
        response_content +=  "  <BR> AP Destination: " + autoPilotDestination.getLabel()
    else:
        response_content +=  "  <BR> AP Destination: None"
    response_content +=  "  <BR> Perspective: " + perspectiveX + ", " + perspectiveY
    
    response_content +=  "  <BR>" + renderActions(self)
    response_content +=  "\n <BR><BR><BR><BR><BR>\n "
    return response_content

def renderStyles(self):
    response_content =  "\n<style>"
    response_content +=  "\n .shad { opacity: .1;  position: absolute; border: 1px solid black;     "
    response_content +=  "\n  border-" + perspectiveX + ": " + str(perspectiveTopPad) + "px solid black; border-" + perspectiveY + ": " + str(perspectiveTopPad) + "px solid black;  "
    response_content +=  "\n } "
    response_content +=  "\n   </style>\n"
    return response_content

def renderMap(self):    
    top=0
    left = 0
    classes = ""
    response_content = "\n<div class='.worldlayer' style='position: absolute; width: " + str(world.x * blocksize) + "px;  height: " + str(world.y * blocksize) + "px'>"
    for checkz in range(world.z +5):
        z = world.z - checkz
       # response_content +=  "\n<div class='.worldlayer' style='position: absolute; width: " + str(world.x * blocksize) + "px;  height: " + str(world.y * blocksize) + "px'>"
        for objs in knownObjs:
            if (objs.z==checkz):
                response_content +=  objs.renderIt() 
       # response_content +=  "\n</div> "
    response_content +=  "\n</div> "
    return response_content



def seedWorld():
    global world
    global drone
    global base
    global knownObjs
    global action
    global droneActions
    global theWorld
    
    world = spacialObject("world",35,80,15)
    aPath=[]
    theWorld=[]
 
    
    knownObjs = []
 
            
    worldPoint = spacialObject("ground",1,1, 0, world.x, world.y, 1)
    addKnownObject(worldPoint) 
    createObstacles()

    drone = spacialObject("drone",2,3,3)        
    base = spacialObject("base",2,3,2)
    addKnownObject(drone)
    addKnownObject(base)
    action=""
    droneActions="Randomizing world"
     
     
seedWorld()

def handleDroneMovement():
    
       
        
        global longTermGoalAchieved
        global droneActions
        global world
        global query_string
        global action
        global value1
        global value2
        global value3
        global value4
        global value5
        global value6
        global apPath
        global autoPilotDestination
        global perspectiveX
        global perspectiveY
        global maxFlightHeight
        global movementPerformed
        
        movementPerformed=False
        currentMoveX = 0
        currentMoveY = 0
        currentMoveZ = 0
             
        # auto pilot code
        if (autoPilotDestination == None):
             print("No AP destination set")
        else:
             print("AP destination set, navigating to it")
            

            
             movementPerformed=False
             droneActions= ""
             xBlocked=False
             yBlocked=False
             zBlocked=False
             

             
             
             if (autoPilotDestination.x < drone.x):
                if (collisiondetection.getObjectByCoordinate(drone.x - 1,drone.y,drone.z ,knownObjs)==None):
                    currentMoveX = currentMoveX  - 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on x- axis"
                    xBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on x- axis"
                    xBlocked=True
                    
             if (autoPilotDestination.x > drone.x):
                checkPath = collisiondetection.getObjectByCoordinate(drone.x + 1,drone.y,drone.z ,knownObjs)
                if (checkPath==None):
                    currentMoveX = currentMoveX + 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on x+ axis"
                    xBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on x+ axis with " + checkPath.getLabel()
                    xBlocked=True
                
             if (int(autoPilotDestination.y) > drone.y):
                checkPath=collisiondetection.getObjectByCoordinate(drone.x ,drone.y + 1,drone.z,knownObjs )
                if (checkPath==None):
                    currentMoveY = currentMoveY + 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on y+ axis"
                    yBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on y+ axis with " + checkPath.getLabel()
                    yBlocked=True
                    
             if (int(autoPilotDestination.y) < drone.y):
                checkPath=collisiondetection.getObjectByCoordinate(drone.x ,drone.y - 1,drone.z ,knownObjs)
                if (checkPath==None):
                    currentMoveY = currentMoveY - 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on y- axis"
                    yBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on y- axis with " + checkPath.getLabel()
                    yBlocked=True
             
             # if drone is near destination
             if (collisiondetection.isNearXY(drone,autoPilotDestination)==True):
                 #print("Drone near destination")
                 if (int(autoPilotDestination.z) < drone.z):
                    checkPath=collisiondetection.getObjectByCoordinate(drone.x,drone.y,drone.z - 1,knownObjs)
                    if (checkPath==None):
                        droneActions= droneActions + ", Lowering drone to z- destination"
                        movementPerformed=True
                        currentMoveZ = currentMoveZ - 1
                        zBlocked=False
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding collision on z- axis with " + checkPath.getLabel()
                        zBlocked=True
                        
                 if (int(autoPilotDestination.z) > drone.z):
                    checkPath=collisiondetection.getObjectByCoordinate(drone.x,drone.y,drone.z + 1,knownObjs)
                    if (checkPath==None):
                        droneActions= droneActions + ", Raising drone to z+ destination"
                        movementPerformed=True
                        currentMoveZ = currentMoveZ + 1
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding +collision on z+ axis with " + checkPath.getLabel()
                        zBlocked=True
             else:
                #print("Drone NOT near destination")
                if (drone.z < defaultFlightHeight):
                    checkPath=collisiondetection.getObjectByCoordinate(drone.x,drone.y,drone.z + 1,knownObjs)
                    if (checkPath==None and drone.z < maxFlightHeight):
                        currentMoveZ = currentMoveZ + 1
                        movementPerformed=True
                        droneActions= droneActions + ", Gaining elevation z+ to safe flight height"
                        zBlocked=False
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding collision on z+ axis with " + checkPath.getLabel()
                        zBlocked=True
                        
             if (movementPerformed==False):
                 if (xBlocked==True or yBlocked==True):
                     if (zBlocked==False):                         
                        if (collisiondetection.getObjectByCoordinate(drone.x,drone.y,drone.z + 1,knownObjs)==None and (drone.z + 1) < maxFlightHeight):
                            droneActions= droneActions + ", Raising drone z+ to avoid obstacle"
                            movementPerformed=True
                            currentMoveZ =  1
                        else:
                            droneActions= droneActions + ", Drone unable to fly over obstacle"
                            if (collisiondetection.getObjectByCoordinate(drone.x + 1,drone.y,drone.z,knownObjs )==None):
                                droneActions= droneActions + ", x+ axis attempt to avoid collision at max height"
                                movementPerformed=True
                                currentMoveX = 1
                             
                                         
                     else:
                         refreshGUI = False
                         droneActions= droneActions + ", Simple paths blocked" 
                             
                     
                
             if (autoPilotDestination.x == drone.x and autoPilotDestination.y == drone.y and autoPilotDestination.z == drone.z and movementPerformed==False):
                droneActions="Drone has landed, autopilot complete"
                movementPerformed=True
                longTermGoalAchieved=True
                refreshGUI = False


        if movementPerformed==True:
                refreshGUI = True
                    #handle manuel moves. Note this does NOT ensure safety of the destination
        if (action=="move"):
            if (value1=="higher"):
                currentMoveZ = currentMoveZ + 1
            if (value1=="lower"):
                currentMoveZ = currentMoveZ - 1                
            if (value1=="up"):
                currentMoveY = currentMoveY + 1          
            if (value1=="down"):
                currentMoveY = currentMoveY - 1          
            if (value1=="right"):
               currentMoveX = currentMoveX + 1          
            if (value1=="left"):
               currentMoveX = currentMoveX - 1
            movementPerformed=True
            refreshGUI=True
        
        if (1==1):
            thisDestination = spacialObject("appath",drone.x + currentMoveX, drone.y + currentMoveY,drone.z + currentMoveZ)
            novelPath=True
                
            for pathPoint in apPath:
                if (pathPoint.x==(drone.x + currentMoveX) and pathPoint.y==(drone.y + currentMoveY) and pathPoint.z==(drone.z + currentMoveZ)):
                    novelPath=False
                
            if (novelPath ==False and longTermGoalAchieved==False):

                #print("Drone got stuck using auto pilot level 1, switching to level 2")
                performAPLevel2() 
                    
            else:
                if (longTermGoalAchieved==False):
                    apPath.append(thisDestination)
                    droneActions=droneActions + ", Drone found novel path."
                    drone.x=drone.x + currentMoveX
                    drone.y=drone.y + currentMoveY
                    drone.z=drone.z + currentMoveZ
                    
 
                
            removeKnownObjectByName("Drone")

class webRequestHandler(BaseHTTPRequestHandler):
    
    def scriptName(self,url):
        return (url + "?").split("?")[0]
    
    def do_GET(self):
        global requestId
        
        requestId = requestId + 1
        
        #if a file was requested, send that. Otherwise send the UI for the drone.
        thefile = self.scriptName(self.path)
        if (thefile != "/"):
             
            fileExt = filesystem.getFileExt(thefile)
            
            try:
                file_path = os.path.join(os.getcwd(), self.path[1:])
                with open(file_path, 'rb') as file:                    
                    self.send_response(200)
                    self.send_header('Content-type', html.getMimeType(fileExt))
                    self.end_headers()
                    self.wfile.write(file.read())
                    return
            except FileNotFoundError:
                 self.send_response(404)
                 self.send_header('Content-type', 'text/plain')
                 self.end_headers()
                 self.wfile.write("File [" + self.path + "] not found")
                 return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(e).encode())
                return
        
        #request wasnt for a file, send drone UI
        
        global longTermGoalAchieved
        global droneActions
        global world
        global query_string
        global action
        global value1
        global value2
        global value3
        global value4
        global value5
        global value6
        global apPath
        global autoPilotDestination
        global autoPilotDistance
        global perspectiveX
        global perspectiveY
        global totalThreads
        
        longTermGoalAchieved=False
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
         
        parsed_path = urllib.parse.urlparse(self.path)
        query_string = parsed_path.query
        loadQS() 
        
        # make a new random world
        if (action=="randomworld"):
            seedWorld()
                    
        if (action=="ap"):
            
            resetAP()
            autoPilotDestination = spacialObject("apdestination",int(value1), int(value2), int(value3))
            addKnownObject(autoPilotDestination)
        
        if (action=="aplevel2"):
            global currentGoodPaths
            global currentBadPaths
            global aplevel2PathedCoordinates
            
            aplevel2PathedCoordinates=[]
            currentGoodPaths=0
            currentBadPaths=0
            if (autoPilotDestination==None):
                #print("autoPilotDestination is None, creating")
                autoPilotDestination = spacialObject("apdestination",int(value1), int(value2), int(value3))
            performAPLevel2()
             
        if (action=="perspectiveX"): 
            perspectiveX = value1
        
        if (action=="perspectiveY"): 
            perspectiveY = value1
        
        
        response_content=" <html><head><script type='text/javascript' src='/html/drone.js'></script><link rel='stylesheet' href='/html/styles.css'> " + renderScripts(self) + renderStyles(self)  + "</head><body> "
         
        if (action != "getmap"):
            handleDroneMovement()
            response_content +=  renderWorld(self)  + renderMap(self) 
        else:
            response_content =  response_content + renderMap(self) 
         
            response_content +=  debugStatements
            response_content +=  "</body></html>"
        self.wfile.write(response_content.encode())

def makeViewPort():
    global viewPort

    # Create initial viewport
    viewPort = spacialObject("viewPort", 1, 1, 1)

    # Calculate X range
    viewPort.x = min(drone.x, world.x)
    viewPort.width = abs(drone.x - world.x)

    # Calculate Y range
    viewPort.y = min(drone.y, world.y)
    viewPort.height = abs(drone.y - world.y)

    # Ensure minimum margins
    viewPort.x = max(1, viewPort.x - 3)
    viewPort.y = max(1, viewPort.y - 3)

    # Expand viewport for margin buffer
    viewPort.width += 6
    viewPort.height += 6


def performAPLevel2():
            makeViewPort()
            global branchCounter
            branchCounter = 0
    
            global mostEfficient 
            global mostEfficientRoute
            global autoPilotDistance
            global autoPilotDestination
            global threads
            global totalThreads
            global goodPathsLimit
            global currentGoodPaths
            global currentBadPaths
            global aplevel2PathedCoordinates
            global useThreads
            global APMovementMode
            global maxApDeviation
            
            if (autoPilotDestination == None):
                #print("No destination set")
                return
            
            branchCounter = 0
            mostEfficient = 99999999
            mostEfficientRoute = []
            
            threads = []
            totalThreads=0
            
          
            currentGoodPaths = 0
            currentBadPaths = 0
            aplevel2PathedCoordinates=[]
            
            level2ApPathsList=[]
            aplevel2PathedCoordinates = []
            threads.clear()
            totalThreads=0
            #apDestination=spacialObject("apdestination",int(value1),int(value2), int(value3))
            if (autoPilotDestination == None):
                print("No destination set")
                return
            else:
                
                autoPilotDistance = collisiondetection.distanceBetweenObjects(drone,autoPilotDestination)
                maxApDeviation=autoPilotStepLimit * autoPilotDistance
                
                newPath = spacialObject("ap",drone.x, drone.y, drone.z)
                startPath=[]
                #startPath.append(newPath)
                addPossiblePath( newPath, startPath, 0)
            
            #while (totalThreads > 0 and currentGoodPaths < goodPathsLimit ):
            if (useThreads==True):
                while (totalThreads > 0 and currentGoodPaths < goodPathsLimit ):
                    print("Total threads left: " + str(totalThreads) + ", autoPilotDistance: " + str(autoPilotDistance) + ", currentGoodPaths: " + str(currentGoodPaths) + ", aplevel2PathedCoordinates: " + str(len(aplevel2PathedCoordinates)) )
                    time.sleep(1)
                for thread in threads:
                    thread.join()
            else:
                print("Total paths left: " + str(len(level2ApPathsList)) + ", autoPilotDistance: " + str(autoPilotDistance) + ", currentGoodPaths: " + str(currentGoodPaths) + ", currentBadPaths: " + str(currentBadPaths) + ", aplevel2PathedCoordinates: " + str(len(aplevel2PathedCoordinates)) )
                
            print("Final Paths: " + str(len(level2ApPathsList)) + ", currentGoodPaths: " + str(currentGoodPaths)  + ", currentBadPaths: " + str(currentBadPaths) + ", len(mostEfficientRoute): " + str(len(mostEfficientRoute)) + ", str(mostEfficient): " + str(mostEfficient))
            apDone =False
         
                 
            if len(mostEfficientRoute) == 0:
                print("Didnt make it to destination")
                refreshGUI = False
            else:
                refreshGUI = True
                print("Made it to destination in " + str(mostEfficient) + " moves")
                print("Path to destination")
                
                for pathCounter in range(1, len(mostEfficientRoute)):
                    print("Step: " + str(pathCounter) + ", " + str(mostEfficientRoute[pathCounter].x) + "," + str(mostEfficientRoute[pathCounter].y) + "," + str(mostEfficientRoute[pathCounter].z))

                #move drone to first step in AP path
                drone.x=mostEfficientRoute[1].x
                drone.y=mostEfficientRoute[1].y
                drone.z=mostEfficientRoute[1].z
                print("Drone moved")
                APMovementMode=True
                
            print("All threads finished")   

def addPossiblePath(co,cp, fb):
    
    currentObj = copy.deepcopy(co)
    currentPath = copy.deepcopy(cp)
    fromBranch = fb
    
    global threads
    global totalThreads
    global autoPilotDistance
    global autoPilotStepLimit
    global level2ApPathsList
    global aplevel2PathedCoordinates
    global useThreads
    global maxApDeviation
    
    if len(currentPath) < (maxApDeviation):
        if (useThreads==True):        
            totalThreads = totalThreads + 1
            #print("launching thread " + str(totalThreads))
            t1 = threading.Thread(target = launchThread, args=(currentObj,currentPath,fromBranch))  #create the thread t1
            #threads.append(t1)
            t1.start()
            return 0
        else:
            alreadMapped=False
            for eachLoc in aplevel2PathedCoordinates:
                if (eachLoc.x==currentObj.x and eachLoc.y==currentObj.y and eachLoc.z==currentObj.z):
                    alreadMapped=True
                    #print("Preventing duplicate branch Dest " + currentObj.getLabel() + " current: " + eachLoc.getLabel() )
                    return
            
            if (alreadMapped==False):    
                #print("Novel branch " + currentObj.getLabel())
                aplevel2PathedCoordinates.append(currentObj)
                newL2Path=possibleAPPath(currentObj,currentPath, fromBranch)
                level2ApPathsList.append(newL2Path)
            #else:
                #print("NOT spawning possibleAPPath")
        
#    else:
#        print("NOT spawning possibleAPPath, out of efficiency allowance")
#        newL2Path=possibleAPPath(copy.deepcopy(fromObj),copy.deepcopy(currentObj),copy.deepcopy(toObj),currentPath.copy())
#        level2ApPathsList.append(newL2Path)

def launchThread(currentObj,currentPath,fromBranch):
    #print("Thread launched")
    global autoPilotDistance
    global autoPilotStepLimit
    global level2ApPathsList
    global totalThreads
    global threads
    global aplevel2PathedCoordinates
    
 
    print("currentObj: " + currentObj.getLabel())
    
    if len(currentPath) < (autoPilotStepLimit * autoPilotDistance):
        #print("spawning possibleAPPath")
        newL2Path=possibleAPPath(copy.deepcopy(currentObj),currentPath.copy(),fromBranch)
        level2ApPathsList.append(newL2Path)
    #else:
        #print("NOT spawning possibleAPPath")
    totalThreads = totalThreads - 1
     

class possibleAPPath():
    def __init__(self, cl,ctp, fromBranch):
        currentLocation = copy.deepcopy(cl)
        copyThisPath = copy.deepcopy(ctp)
        
        
        #print ("new possibleAPPath , current coords: " + str(currentLocation.x) +"," + str(currentLocation.y)  +"," + str(currentLocation.z) )
        global autoPilotDestination
        global autoPilotStepLimit
        global currentGoodPaths
        global currentBadPaths
        global mostEfficient 
        global mostEfficientRoute 
        
        self.branchId=getBranchId()
        self.currentLocation = spacialObject(currentLocation.name,currentLocation.x, currentLocation.y, currentLocation.z)  
        self.recordedPath=copyThisPath           
        self.branchGetsToDestination=False     

        destFile="logs/" + str(requestId) + "_" + str(fromBranch) + "_" + str(branchCounter)  + ".txt"
        filesystem.appendFile(destFile,  "Starting branch, launched from  " + str(fromBranch) + " \n")
        filesystem.appendFile(destFile,  "Drone location: " + drone.getLabel() + " \n")
        filesystem.appendFile(destFile,  "currentLocation: " + currentLocation.getLabel() + " \n")
        filesystem.appendFile(destFile,  "autoPilotDestination: " + autoPilotDestination.getLabel() + " \n")
        filesystem.appendFile(destFile,  "This path: \n")
        filesystem.appendFile(destFile,  self.currentLocation.getLabel() + "\n")
        for eachLoc in copyThisPath:
            filesystem.appendFile(destFile,  eachLoc.getLabel()  + "\n")
        
        if (currentLocation.x== autoPilotDestination.x and currentLocation.y== autoPilotDestination.y and currentLocation.z== autoPilotDestination.z  ):
            print("made it to dest")
            self.branchGetsToDestination=True
            currentGoodPaths = currentGoodPaths + 1
            filesystem.appendFile(destFile,  "Made it to destination! \n")
            
            mostEfficient = 99999999
            mostEfficientRoute = []
            if ( len(self.recordedPath) < mostEfficient):
                mostEfficient=len(self.recordedPath)
                mostEfficientRoute = self.recordedPath
            
            return
        
        
   
         
        filesystem.appendFile(destFile,  "spawned branch " + str(self.branchId) + "," + self.currentLocation.getLabel() + " , steps: " + str(len(self.recordedPath)) + "\n")
        #self.runPath()
  
        # if near the destination, lower
        #if (collisiondetection.isNearXY(self.currentLocation,autoPilotDestination)==True):
        if (self.currentLocation.x==autoPilotDestination.x and self.currentLocation.y==autoPilotDestination.y and self.currentLocation.z>autoPilotDestination.z):
           
             self.checkLocation(self.currentLocation.x,self.currentLocation.y,self.currentLocation.z-1,destFile)
            
        else:
            #if near the take off point, then focus on gaining altitude before moving
            #if (self.currentLocation.z < defaultFlightHeight):
            if (self.currentLocation.z < defaultFlightHeight):
                filesystem.appendFile(destFile,  "drone is below ideal flight height, raising \n")
                self.checkLocation(self.currentLocation.x,self.currentLocation.y,self.currentLocation.z+1,destFile)
                return
                #self.checkLocation(self.currentLocation.x,self.currentLocation.y,self.currentLocation.z-1)
                
    
        self.checkLocation(self.currentLocation.x+1,self.currentLocation.y,self.currentLocation.z,destFile)
         
        self.checkLocation(self.currentLocation.x-1,self.currentLocation.y,self.currentLocation.z,destFile)
         
        self.checkLocation(self.currentLocation.x,self.currentLocation.y+1,self.currentLocation.z,destFile)
         
        self.checkLocation(self.currentLocation.x,self.currentLocation.y-1,self.currentLocation.z,destFile)
                
        currentBadPaths = currentBadPaths + 1
        
    def checkLocation(self,x,y,z, destFile):
        newpath = copy.deepcopy(self.currentLocation)
        newpath.x=x
        newpath.y=y
        newpath.z=z
        newpath.id=len(self.recordedPath)+1
        newpath.note="Added by BranchId: " + str(self.branchId) + ", Distance to destination: " + str(collisiondetection.distanceBetweenObjects(newpath,autoPilotDestination))  + ", maxApDeviation: " + str(maxApDeviation)
        #print("adding new location to path")
        
        
        filesystem.appendFile(destFile,  "checking location " + newpath.getLabel() + " \n")
            
        global knownObjs
        global currentBadPaths
        
        for eachLocation in self.recordedPath:
            if (eachLocation.x== newpath.x and eachLocation.y== newpath.y and eachLocation.z== newpath.z):
                #print("already moved here [" + str(newpath.x) + "," + str(newpath.y) + "," + str(newpath.z) + " ], killing branch ")
                filesystem.appendFile(destFile,  "Already moved to this location in this branch " + newpath.getLabel() + " \n")
                currentBadPaths = currentBadPaths + 1
                return
            
        self.recordedPath.append(newpath)
        
        if (newpath.x < 1 or newpath.y < 1  or newpath.z < 1 ):
            filesystem.appendFile(destFile,  "Out of bounds" + newpath.getLabel() + " \n")
            return 0

        if ( newpath.x > world.x ):
            filesystem.appendFile(destFile,  "Out of bounds" + newpath.getLabel() + " \n")
            return 0
        if ( newpath.y > world.y ):
            filesystem.appendFile(destFile,  "Out of bounds" + newpath.getLabel() + " \n")
            return 0
        if ( newpath.z > world.z):
            filesystem.appendFile(destFile,  "Out of bounds" + newpath.getLabel() + " \n")
            return 0

        global viewPort
        
        filesystem.appendFile(destFile,  "viewPort: " + viewPort.getLabel() + " \n")
         
        if (newpath.x < viewPort.x    ):
            filesystem.appendFile(destFile,  "Out of viewPort x1" + newpath.getLabel() + " \n")
            return 0
        if ( newpath.y < viewPort.y   ):
            filesystem.appendFile(destFile,  "Out of viewPort y1" + newpath.getLabel() + " \n")
            return 0
        

        if ( newpath.x > viewPort.x2() ):
            filesystem.appendFile(destFile,  "Out of viewPort x2" + newpath.getLabel() + " \n")
            return 0
        if ( newpath.y > viewPort.y2() ):
            filesystem.appendFile(destFile,  "Out of viewPort y2" + newpath.getLabel() + " \n")
            return 0


        
        checkLoc=collisiondetection.getObjectByCoordinate(newpath.x,newpath.y,newpath.z,knownObjs)
        if (checkLoc==None):
            filesystem.appendFile(destFile,  "Adding possible path" + newpath.getLabel() + " \n")
            #print("New path - spawning branch coords: " + str(self.currentLocation.x) + "," + str(self.currentLocation.y) + "," + str(self.currentLocation.z))
            addPossiblePath(newpath, self.recordedPath, self.branchId)
            return 1
        else:
            filesystem.appendFile(destFile,  "Hit object " + checkLoc.getLabel() + " \n")
        #else:
            #print("avoiding object - killing branch")



def run(server_class=HTTPServer, handler_class=webRequestHandler, port=8001):
   server_address = ('', port)
   httpd = server_class(server_address, handler_class)
   print(f"Starting server on port {port}...")
   httpd.serve_forever()
  
if __name__ == '__main__':
   run()