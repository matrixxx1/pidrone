import random
import http
from http.server import BaseHTTPRequestHandler, HTTPServer

import urllib.parse
 

import helpers_html as html
import helpers_collisiondetection as collisiondetection 


#this determines how the world will be rendered to the browser
perspectiveX="right"    #left or right
perspectiveY="top"  #top or bottom


blocksize = 14 #how many pixels wide and tall a block is in the world. a block represents a cubic meter
padtop= 10 # where to start rendering the world on the up/down axis
padleft=50 # where to start rendering the world on the left/right axis

#when rendering to imply height difference, how much shift should occur
perspectiveTopPad = blocksize / 4 # up/down
perspectiveLeftPad = blocksize / 4  #left/right
       
      
defaultFlightHeight = 10 # prefered height that the drone should fly
maxFlightHeight = 15 # max height the drone is allowed to achieve





class obj():
    def __init__(self, name, x, y,z, objHeight=1, objWidth=1, objDepth=1):
        self.name=name
        self.x = x
        self.y = y
        self.z= z
        self.height=objHeight
        self.width=objWidth
        self.depth=objDepth
        self.id=0
        
    def x1(self):
        return int(self.x)
        
    def y1(self):
        return int(self.y )
    
    def z1(self):
        return int(self.z )
    
    def x2(self):
        return int(self.x) + int(self.width)
        
    def y2(self):
        return int(self.y) + int(self.height)
    
    def z2(self):
        return int(self.z) - int(self.depth)
    
    def getLabel(self):
        return self.name + " coords: x: " + str(self.x) +", y: " + str(self.y) + ", z: " + str(self.z) + " size: x: " + str(self.width) +", y: " + str(self.height) + ", z: " + str(self.depth)  + ", id: " + str(self.id)

    def renderIt(self):
        global perspectiveX
        global perspectiveY
        
   
            
        retval = ""
         
        #render extra divs to give it a 3d look
        #if (self.name!="ground" and self.name!="drone" and self.name!="base"):
            #retval = retval + "\n<div  style='top: " + str(int(top+6)) + "; left: " + str(int(left +6)) + "; z-index: " + str(int(self.z)) + "; ' class='shad'></div>\n"
            #retval = retval + "\n<div  style='top: " + str(int(top+4)) + "; left: " + str(int(left +4)) + "; z-index: " + str(int(self.z)) + "; width: " + str(int(blocksize) * self.width) + "px; height: " + str(int(blocksize) * self.height) + "px;' class='shad'></div>\n"
            #retval = retval + "\n<div  style='top: " + str(int(top+2)) + "; left: " + str(int(left +2)) + "; z-index: " + str(int(self.z)) + "; ' class='shad'></div>\n"
        
        #render divs to give it depth
        if (self.name!="ground"):
            for objectLayer in range( self.z - self.depth , self.z ):
                renderLayer= self.z - objectLayer
                top = padtop  + (self.x * blocksize)   + shiftTopPerspectiveByLayer(objectLayer) 
                left = padleft + (self.y  * blocksize)   + shiftLeftPerspectiveByLayer(objectLayer) 
                retval = retval + "\n<div  title='Shadow-" + str(renderLayer) + ": " + self.getLabel() + "'   style='top: " + str(int(top)) + "; left: " + str(int(left)) + "; z-index: " + str(int(renderLayer)) + "; width: " + str(int(blocksize) * self.width) + "px; height: " + str(int(blocksize) * self.height) + "px; ' class='shad'></div>\n"
         
        #render the actual object
       
        top = padtop  + (self.x * blocksize)   + shiftTopPerspectiveByLayer(self.z) 
        left = padleft + (self.y  * blocksize)   + shiftLeftPerspectiveByLayer(self.z) 
         
        retval = retval + "\n <div   onclick='sD(" + str(self.x) + "," + str(self.y) +  "," + str(self.z + 1) + ")' title='Object: " + self.getLabel() + "' "
        retval = retval + " style='position: absolute; top: " + str(top) + ";   left: " + str(left) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " width: " + str(int(blocksize) * self.width) + "px; height: " + str(int(blocksize) * self.height) + "px;'   class='mo " + self.name + "'></div>" 

        return retval



         

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
autoPilotDestination = obj("apdestination",0,0,0,"")
base="" 
 

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
            addKnownObject(obj("tree",thex  ,they ,treeHeightRND))
            #create growing layers until hitting ground
            for thisLayerRange in range(thisLevel -1):
                if (treeHeight < treeTrunkHeightRND):
                    #create trunk
                    addKnownObject(obj("treetrunk",thex ,they ,treeHeight))
                else:
                    #create next layer of leaves
                    addKnownObject(obj("tree",thex + thisLayerRange ,they ,treeHeight))
                    addKnownObject(obj("tree",thex - thisLayerRange ,they ,treeHeight))
                    addKnownObject(obj("tree",thex  ,they + thisLayerRange,treeHeight))
                    addKnownObject(obj("tree",thex  ,they - thisLayerRange,treeHeight))
            
    # make some random walls
    for wallCounter in range(1,random.randint(4, 10)):
        rndHeight= random.randint(4, maxFlightHeight) 
        addKnownObject(obj("wall",random.randint(4, 30) ,random.randint(4, 30) ,rndHeight ,random.randint(1, 5) ,random.randint(1, 5) , rndHeight ))    
                
   # #make a few large walls that can be flown over
   # for theheight in range(10):
   #     for wall in range(15):
   #         addKnownObject(obj("wall",wall,15,theheight+1))
   #         addKnownObject(obj("wall",wall + 5,19,theheight+1))
    addKnownObject(obj("wall",7,5,5,15,1,4))
    addKnownObject(obj("wall",17,15,5,15,1,4))
    
    addKnownObject(obj("poi",35,15,2))
    addKnownObject(obj("poi",35,30,2))
    addKnownObject(obj("poi",35,45,2))
    addKnownObject(obj("poi",35,50,2))
    addKnownObject(obj("poi",35,75,2))
    
    addKnownObject(obj("poi",5,15,2))
    addKnownObject(obj("poi",5,30,2))
    addKnownObject(obj("poi",5,45,2))
    addKnownObject(obj("poi",5,50,2))
    addKnownObject(obj("poi",5,75,2))
            
#make large walls that cant be flown over
    #for theheight in range(defaultFlightHeight + 5):
    addKnownObject(obj("wall",15,25,maxFlightHeight ,15,1,maxFlightHeight ))     
    addKnownObject(obj("wall",24,5,maxFlightHeight ,1,25, maxFlightHeight ))
    addKnownObject(obj("wall",20,10,maxFlightHeight ,1,25, maxFlightHeight ))          
    addKnownObject(obj("wall",15,15,maxFlightHeight ,1,25, maxFlightHeight ))    
    
    
        
        
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
        action=""
        value1 = ""
        value2 = ""
        value3 = ""
        value4 = ""
        value5 = ""
        value6 = ""
        autoPilotDestination=None
        
        removeKnownObjectByName("apdestination")
         
            
            
    retval = retval + "\n <BR>Drone actions: " + droneActions + "<BR><BR>"
    retval = retval + html.makeLink("/?action=move&value=left","<") + " | "  + html.makeLink("/?action=move&value=right",">") + " | "
    retval = retval + html.makeLink("/?action=move&value=up","/\\") + " | " + html.makeLink("/?action=move&value=down","\\/") + " | "
    retval = retval + html.makeLink("/?action=move&value=higher","Raise") + " | "  + html.makeLink("/?action=move&value=lower","Lower") + " | "
    retval = retval + html.makeLink("/?action=randomworld","Randomize World") + " | "
    retval = retval + html.makeLink("/?action=perspectiveX&value1=left","perspective left") + " | "
    retval = retval + html.makeLink("/?action=perspectiveX&value1=right","perspective right") + " | "
    retval = retval + html.makeLink("/?action=perspectiveY&value1=top","perspective top") + " | "
    retval = retval + html.makeLink("/?action=perspectiveY&value1=bottom","perspective bottom") + " | "
 
    
    retval = retval + "\n<BR><BR> " + html.makeInput("action","ip",action)
    retval = retval + html.makeInput("value1","ip",value1)  + html.makeInput("value2","ip",value2)
    retval = retval + html.makeInput("value3","ip",value3)  + html.makeInput("value4","ip",value4)
    retval = retval + html.makeInput("value5","ip",value5) + html.makeInput("value6","ip",value6)
    
    
    retval = retval + "\n <input type='button' value='run' onclick='subForm();'>\n "
    return retval

def renderScripts(self):
    retval = "\n <script>  "
    retval = retval + "\n window.droneX=" + str(drone.x)
    retval = retval + "\n window.droneY=" + str(drone.y)
    retval = retval + "\n window.droneZ=" + str(drone.z)
    retval = retval + "\n function sD(x,y,z){  window.location.href='/?action=ap&value1=' + x + '&value2=' + y + '&value3=' + z  + '&value4=' + window.droneX  + '&value5=' + window.droneY  + '&value6=' + window.droneZ;}  \n"
    retval = retval + "\n function getIt(frmName){ return document.getElementById(frmName).value; }  \n"
    retval = retval + "\n function subForm(){ window.location.href='/?action=' + getIt(\"action\") + '&value1=' + getIt(\"value1\") + '&value2=' + getIt(\"value2\") + '&value3=' + getIt(\"value3\") + '&value4=' + getIt(\"value4\") + '&value5=' + getIt(\"value5\") + '&value6=' + getIt(\"value6\"); } \n"
    retval = retval + "\n function autoPilot(){ if (getIt(\"action\")==\"ap\"){subForm();}} \n"
    retval = retval + "\n setTimeout(autoPilot, 2000); \n </script>"
    return retval

def renderWorld(self):
    #let timeoutId = setTimeout(greet, 2000, "World")
    response_content = "<BR>" + drone.getLabel() + "<BR> World Size - x: " + str(world.x) + ", y: " + str(world.y) + ", z: " + str(world.z)
    response_content = response_content + "  <BR> Known objects: " + str(len(knownObjs))
    response_content = response_content + "  <BR> AP Destination: " + autoPilotDestination.getLabel()
    response_content = response_content + "  <BR> Perspective: " + perspectiveX + ", " + perspectiveY
    
    response_content = response_content + "  <BR>" + renderActions(self)
    response_content = response_content + "\n <BR><BR><BR><BR><BR>\n <style>"
    response_content = response_content + "\n .tree { background-color: green; opacity: .3; } "
    response_content = response_content + "\n .poi { background-color: yellow; opacity: 1; } "
    response_content = response_content + "\n .treetrunk { background-color: brown; opacity: .3;  } "
    response_content = response_content + "\n .drone { background-color: blue; opacity: 1;  } "
    response_content = response_content + "\n .base { background-color: red; opacity: 1;  } "
    response_content = response_content + "\n .apdestination { background-color: yellow; opacity: 1;  } "
    response_content = response_content + "\n .wall { background-color: white; opacity: .3;  } "
    response_content = response_content + "\n .ground { background-color: gray; opacity: 1;  } "
    #transform-style: preserve-3d; transform: translateY(-10px) rotateX(65deg);    
    response_content = response_content + "\n .worldlayer { position: absolute; border: 1px dashed black;     } "
    response_content = response_content + "\n .mo {   position: absolute;   border: 1px solid black; border-bottom: 2px solid black; border-right: 2px solid black;  } "
    response_content = response_content + "\n .shad { opacity: .1;  position: absolute; border: 1px solid black;     "

    response_content = response_content + "\n  border-" + perspectiveX + ": " + str(perspectiveTopPad) + "px solid black; border-" + perspectiveY + ": " + str(perspectiveTopPad) + "px solid black;  "
    response_content = response_content + "\n } "
    response_content = response_content + "\n   .ip {   width: 60px;   } </style>"

    
    
    top=0
    left = 0
    classes = ""
    response_content = response_content + "\n<div class='.worldlayer' style='position: absolute; width: " + str(world.x * blocksize) + "px;  height: " + str(world.y * blocksize) + "px'>"
    for checkz in range(world.z +5):
        z = world.z - checkz
       # response_content = response_content + "\n<div class='.worldlayer' style='position: absolute; width: " + str(world.x * blocksize) + "px;  height: " + str(world.y * blocksize) + "px'>"
        for objs in knownObjs:
            if (objs.z==checkz):
                response_content = response_content + objs.renderIt() 
       # response_content = response_content + "\n</div> "
    response_content = response_content + "\n</div> "
    return response_content



def seedWorld():
    global world
    global drone
    global base
    global knownObjs
    global action
    global droneActions
    global theWorld
    
    world = obj("world",35,80,15,"")
    aPath=[]
    theWorld=[]
    #for y in range(world.y):
    #    for x in range(world.x):
    #        for z in range(world.z):
    #            worldPoint = obj("",x,y,world.z - z,"")
    #            theWorld.append(worldPoint)
    
    knownObjs = []
    #for y in range(world.y):
    #    for x in range(world.x):
    #        worldPoint = obj("ground",x,y,1, world.x, world.y)
    #        addKnownObject(worldPoint)
            
    worldPoint = obj("ground",1,1, 0, world.x, world.y, 1)
    addKnownObject(worldPoint) 
    createObstacles()

    drone = obj("drone",2,3,3)        
    base = obj("base",2,3,2)
    addKnownObject(drone)
    addKnownObject(base)
    action=""
    droneActions="Randomizing world"
     
     
seedWorld()



class webRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
        
        longTermGoalAchieved=False
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
         
        parsed_path = urllib.parse.urlparse(self.path)
        query_string = parsed_path.query
        loadQS() 
       
        currentMoveX = 0
        currentMoveY = 0
        currentMoveZ = 0
         
         
        # make a new random world
        if (action=="randomworld"):
            seedWorld()
            
        
        if (action=="ap"):
            autoPilotDestination = obj("apdestination",value4, value5, value6)
            addKnownObject(autoPilotDestination)
            
        # auto pilot code
        if (action=="ap"):
             movementPerformed=False
             droneActions= ""
             xBlocked=False
             yBlocked=False
             zBlocked=False
             

             
             
             if (int(value1) < drone.x):
                if (collisiondetection.safeToMove(drone.x - 1,drone.y,drone.z ,maxFlightHeight,knownObjs)==True):
                    currentMoveX = currentMoveX  - 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on x- axis"
                    xBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on x- axis"
                    xBlocked=True
                    
             if (int(value1) > drone.x):
                if (collisiondetection.safeToMove(drone.x + 1,drone.y,drone.z ,maxFlightHeight,knownObjs)==True):
                    currentMoveX = currentMoveX + 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on x+ axis"
                    xBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on x+ axis"
                    xBlocked=True
                
             if (int(value2) > drone.y):
                if (collisiondetection.safeToMove(drone.x ,drone.y + 1,drone.z,maxFlightHeight,knownObjs )==True):
                    currentMoveY = currentMoveY + 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on y+ axis"
                    yBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on y+ axis"
                    yBlocked=True
                    
             if (int(value2) < drone.y):
                if (collisiondetection.safeToMove(drone.x ,drone.y - 1,drone.z ,maxFlightHeight,knownObjs)==True):
                    currentMoveY = currentMoveY - 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on y- axis"
                    yBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on y- axis"
                    yBlocked=True
             
             # if drone is near destination
             if (collisiondetection.isNearXY(drone,obj("dest",int(value1),int(value2),int(value3),""))==True):
                 
                 if (int(value3) < drone.z):
                    if (collisiondetection.safeToMove(drone.x,drone.y,drone.z - 1,maxFlightHeight,knownObjs)==True):
                        droneActions= droneActions + ", Lowering drone to z- destination"
                        movementPerformed=True
                        currentMoveZ = currentMoveZ - 1
                        zBlocked=False
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding collision on z- axis"
                        zBlocked=True
                        
                 if (int(value3) > drone.z):
                    if (collisiondetection.safeToMove(drone.x,drone.y,drone.z + 1,maxFlightHeight,knownObjs)==True):
                        droneActions= droneActions + ", Raising drone to z+ destination"
                        movementPerformed=True
                        currentMoveZ = currentMoveZ + 1
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding +collision on z+ axis"
                        zBlocked=True
             else:
                if (drone.z < defaultFlightHeight):
                    if (collisiondetection.safeToMove(drone.x,drone.y,drone.z + 1,maxFlightHeight,knownObjs)==True):
                        currentMoveZ = currentMoveZ + 1
                        movementPerformed=True
                        droneActions= droneActions + ", Gaining elevation z+ to safe flight height"
                        zBlocked=False
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding collision on z+ axis"
                        zBlocked=True
                        
             if (movementPerformed==False):
                 if (xBlocked==True or yBlocked==True):
                     if (zBlocked==False):                         
                        if (collisiondetection.safeToMove(drone.x,drone.y,drone.z + 1,maxFlightHeight,knownObjs)==True):
                            droneActions= droneActions + ", Raising drone z+ to avoid obstacle"
                            movementPerformed=True
                            currentMoveZ =  1
                        else:
                            droneActions= droneActions + ", Drone unable to fly over obstacle"
                            if (collisiondetection.safeToMove(drone.x + 1,drone.y,drone.z,maxFlightHeight,knownObjs )==True):
                                droneActions= droneActions + ", x+ axis attempt to avoid collision at max height"
                                movementPerformed=True
                                currentMoveX = 1
                            else:
                                if (collisiondetection.safeToMove(drone.x - 1,drone.y,drone.z ,maxFlightHeight,knownObjs)==True):
                                    droneActions= droneActions + ", x- axis attempt to avoid collision at max height"
                                    movementPerformed=True
                                    currentMoveX = -1
                                else:
                                    droneActions= droneActions + ", Unable to use x axis to avoid obstacle"
                                    if (collisiondetection.safeToMove(drone.x,drone.y + 1,drone.z,maxFlightHeight,knownObjs)==True):
                                        droneActions= droneActions + ", y+ axis attempt to avoid collision at max height"
                                        movementPerformed=True
                                        currentMoveY =  1
                                    else:
                                        if (collisiondetection.safeToMove(drone.x,drone.y-1,drone.z,maxFlightHeight,knownObjs)==True):
                                            droneActions= droneActions + ", y- axis attempt to avoid collision at max height"
                                            movementPerformed=True
                                            currentMoveY =  -1
                                        else:
                                            droneActions= droneActions + ",  All paths x,y,z blocked - Good luck!"
                                            movementPerformed=True
                                         
                     else:
                         droneActions= droneActions + ", All paths blocked" 
                             
                     
                
             if (int(value1) == drone.x and int(value2) == drone.y and int(value3) == drone.z and movementPerformed==False):
                droneActions="Drone has landed, autopilot complete"
                movementPerformed=True
                longTermGoalAchieved=True                
        
        if (action=="perspectiveX"): 
            perspectiveX = value1
        if (action=="perspectiveY"): 
            perspectiveY = value1
            
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
        
        
        
        thisDestination = obj("appath",drone.x + currentMoveX, drone.y + currentMoveY,drone.z + currentMoveZ,"")
        novelPath=True
        
        for pathPoint in apPath:
            if (pathPoint.x==(drone.x + currentMoveX) and pathPoint.y==(drone.y + currentMoveY) and pathPoint.z==(drone.z + currentMoveZ)):
                novelPath=False
        
        if (novelPath ==False and longTermGoalAchieved==False):
            #caught in loop
            droneActions=droneActions + ", Drone has gotten stuck, autopilot failed."
            if (currentMoveX > 0):
                droneActions=droneActions + ", Drone has gotten stuck x+, autopilot failed."
                #moving right, set short term goal
            if (currentMoveX < 0):
                droneActions=droneActions + ", Drone has gotten stuck x-, autopilot failed."
                #moving left, set short term goal
            if (currentMoveY > 0):
                droneActions=droneActions + ", Drone has gotten stuck y+, autopilot failed."
                #moving down, set short term goal
            if (currentMoveY < 0):
                droneActions=droneActions + ", Drone has gotten stuck y-, autopilot failed."
                #moving up, set short term goal
        
            
        else:
            if (longTermGoalAchieved==False):
                apPath.append(thisDestination)
                droneActions=droneActions + ", Drone found novel path."
                drone.x=drone.x + currentMoveX
                drone.y=drone.y + currentMoveY
                drone.z=drone.z + currentMoveZ
        
        print("APPATH")
        print(len(apPath))
        
        removeKnownObjectByName("Drone")
        
        #knownObjs.pop(0)
        #knownObjs.insert(0,drone)

        response_content = renderScripts(self) + renderWorld(self) 
                 
        #response_content = "<html><body><h1>Hello, World!</h1></body></html>"
        self.wfile.write(response_content.encode())

apPath = []
apPath.append(obj("appath",0, 0,0,""))

def removeKnownObjectByName(objName):
    global knownObjs
    for eachObj in knownObjs:
        if (eachObj.name==objName):
            knownObjs.remove(eachObj)

def run(server_class=HTTPServer, handler_class=webRequestHandler, port=8001):
   server_address = ('', port)
   httpd = server_class(server_address, handler_class)
   print(f"Starting server on port {port}...")
   httpd.serve_forever()
  
if __name__ == '__main__':
   run()