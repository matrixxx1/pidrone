import random
import http
from http.server import BaseHTTPRequestHandler, HTTPServer

import urllib.parse
 

import helpers_html as html

#this determines how the world will be rendered to the browser
perspectiveX="left"    #left or right
perspectiveY="bottom"  #top or bottom


blocksize = 14 #how many pixels wide and tall a block is in the world. a block represents a cubic meter
padtop= 70 # where to start rendering the world on the up/down axis
padleft=70 # where to start rendering the world on the left/right axis

#when rendering to imply height difference, how much shift should occur
heightpad = blocksize / 2 # up/down
leftpad = blocksize      /2   #left/right
       
      
defaultFlightHeight = 10 # prefered height that the drone should fly
maxFlightHeight = 15 # max height the drone is allowed to achieve


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
base="" 
 
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
     

class obj():
    def __init__(self, name, x, y,z, color):
        self.name=name
        self.x = x
        self.y = y
        self.z= z
        self.color=color
        
    def getLabel(self):
        return self.name + " coords: x: " + str(self.x) +", y: " + str(self.y) + ", z: " + str(self.z)

    def renderIt(self):
        global perspectiveX
        global perspectiveY
        
        left = (self.y  * blocksize)  + padleft
        top = (self.x * blocksize)   + padtop
        
        if (perspectiveX=="right"):            
            left = (self.y  * blocksize)  + padleft - (self.z  * leftpad)
        if (perspectiveX=="left"):            
            left = (self.y  * blocksize)  + padleft + (self.z  * leftpad)
        if (perspectiveY=="top"):
            top = (self.x * blocksize)   + padtop + (self.z * heightpad)             
        if (perspectiveY=="bottom"):
            top = (self.x * blocksize)   + padtop - (self.z * heightpad)
            
        retval = ""
        opacity=".1"
        if (self.name=="drone" or self.name=="ground" or self.name=="base"):
            opacity="1"
        
        #render extra divs to give it a 3d look
        if (self.name!="ground" and self.name!="drone" and self.name!="base"):
            retval = retval + "\n<div  style='opacity: " + opacity + "; position: absolute; top: " + str(top+6) + "; left: " + str(left +6) + "; z-index: " + str(self.z) + "; background-color: " + self.color + ";' class='shad'></div>\n"
            retval = retval + "\n<div  style='opacity: " + opacity + "; position: absolute; top: " + str(top+4) + "; left: " + str(left +4) + "; z-index: " + str(self.z) + "; background-color: " + self.color + ";' class='shad'></div>\n"
            retval = retval + "\n<div  style='opacity: " + opacity + "; position: absolute; top: " + str(top+2) + "; left: " + str(left +2) + "; z-index: " + str(self.z) + "; background-color: " + self.color + ";' class='shad'></div>\n"
            opacity=".5"
        
        #render the actual object
        retval = retval + "\n <div onclick='setDest(" + str(self.x) + "," + str(self.y) +  "," + str(self.z + 1) + ")' title='name: " + self.name + ", x: " + str(self.x) +", y: " + str(self.y) + ", z: " + str(self.z) + "' "
        retval = retval + " style='opacity: " + opacity + "; position: absolute; top: " + str(top) + ";   left: " + str(left) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " background-color: " + self.color + ";'   class='mcellobj'></div>" 

        return retval
 
def addKnownObject(theObj):
    global knownObjs
    knownObjs.append(theObj)
    
  

def createObstacles():
   
    #make some trees
    howManyTrees = random.randint(2, 7)
    for treeLoop in range(howManyTrees):
        thex = random.randint(1, world.x -1)
        they = random.randint(1, world.y -1)
        treeHeightRND = random.randint(5, world.z -1) 
        
        for thisLevel in range(treeHeightRND):
            treeHeight = treeHeightRND - thisLevel
            # place top of tree
            addKnownObject(obj("tree",thex  ,they ,treeHeightRND,"green"))
            #create growing layers until hitting ground
            for thisLayerRange in range(thisLevel -1):
                #create next layer
                addKnownObject(obj("tree",thex + thisLayerRange ,they ,treeHeight,"green"))
                addKnownObject(obj("tree",thex - thisLayerRange ,they ,treeHeight,"green"))
                addKnownObject(obj("tree",thex  ,they + thisLayerRange,treeHeight,"green"))
                addKnownObject(obj("tree",thex  ,they - thisLayerRange,treeHeight,"green"))
            
             
                
    #make a few large walls that can be flown over
    for theheight in range(10):
        for wall in range(15):
            addKnownObject(obj("wall",wall,15,theheight+1,"white"))
            addKnownObject(obj("wall",wall + 5,19,theheight+1,"white"))

#make large walls that cant be flown over
    for theheight in range(defaultFlightHeight + 5):
        for wall in range(15):
            addKnownObject(obj("wall",wall,25,theheight+1,"white"))
            addKnownObject(obj("wall",wall + 10,21,theheight+1,"white"))   
            addKnownObject(obj("wall",wall + 10,28,theheight+1,"white"))
    for theheight in range(defaultFlightHeight + 5):
            addKnownObject(obj("wall",24,22,theheight+1,"white"))
            addKnownObject(obj("wall",24,23,theheight+1,"white"))
            addKnownObject(obj("wall",24,24,theheight+1,"white"))
            addKnownObject(obj("wall",24,25,theheight+1,"white"))
            addKnownObject(obj("wall",24,26,theheight+1,"white"))
            addKnownObject(obj("wall",24,27,theheight+1,"white"))
            
def safeToMove(x,y,z):
    if (z> maxFlightHeight):
        return False
    for objs in knownObjs:
        if (objs.name!="drone"):
            if (objs.x==x and objs.y==y and objs.z==z):
                print("Near collision with " + objs.getLabel())
                return False
    return True
    
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
    
    retval = retval + "\n <BR>Drone actions: " + droneActions + "<BR><BR>"
    retval = retval + html.makeLink("/?action=move&value=left","<") + " | "  + html.makeLink("/?action=move&value=right",">") + " | "
    retval = retval + html.makeLink("/?action=move&value=up","/\\") + " | " + html.makeLink("/?action=move&value=down","\\/") + " | "
    retval = retval + html.makeLink("/?action=move&value=higher","Raise") + " | "  + html.makeLink("/?action=move&value=lower","Lower") + " | "
    retval = retval + html.makeLink("/?action=randomworld","Randomize World") + " | "
    
 
    
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
    retval = retval + "\n function setDest(x,y,z){  window.location.href='/?action=ap&value1=' + x + '&value2=' + y + '&value3=' + z  + '&value4=' + window.droneX  + '&value5=' + window.droneY  + '&value6=' + window.droneZ;}  \n"
    retval = retval + "\n function getIt(frmName){ return document.getElementById(frmName).value; }  \n"
    retval = retval + "\n function subForm(){ window.location.href='/?action=' + getIt(\"action\") + '&value1=' + getIt(\"value1\") + '&value2=' + getIt(\"value2\") + '&value3=' + getIt(\"value3\") + '&value4=' + getIt(\"value4\") + '&value5=' + getIt(\"value5\") + '&value6=' + getIt(\"value6\"); } \n"
    retval = retval + "\n function autoPilot(){ if (getIt(\"action\")!=\"\"){subForm();}} \n"
    retval = retval + "\n setTimeout(autoPilot, 2000); \n </script>"
    return retval

def renderWorld(self):
    #let timeoutId = setTimeout(greet, 2000, "World")
    response_content = "<BR>" + drone.getLabel() + "<BR> World Size - x: " + str(world.x) + ", y: " + str(world.y) + ", z: " + str(world.z) + "  <BR>" + renderActions(self)
    response_content = response_content + "\n<BR><BR><BR><BR><BR>\n"
    response_content = response_content + "\n<style> .mcell {  border: 1px dashed yellow; opacity: 0.8; transform-style: preserve-3d; transform: translateY(-10px) rotateX(65deg);   width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "\n<style> .mcellobj {      border: 1px dashed red; border-bottom: 2px solid black; border-right: 2px solid black; width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "\n<style> .shad {      border-top: 2px solid black; border-left: 2px solid black;  width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "\n<style> .ip {   width: 60px;   } </style>"

    
    
    top=0
    left = 0
    classes = ""        
    for checkz in range(world.z):
        z = world.z - checkz
        response_content = response_content + "\n<div class='.mcell' style='position: absolute; width: " + str(world.x * blocksize) + "px;  height: " + str(world.y * blocksize) + "px'>"
        for objs in knownObjs:
            if (objs.z==z):
                response_content = response_content + objs.renderIt() 
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
    
    world = obj("world",60,30,15,"")
    
    theWorld=[]
    for y in range(world.y):
        for x in range(world.x):
            for z in range(world.z):
                worldPoint = obj("",x,y,world.z - z,"")
                theWorld.append(worldPoint)
    
    knownObjs = []
    for y in range(world.y):
        for x in range(world.x):
            worldPoint = obj("ground",x,y,1,"gray")
            addKnownObject(worldPoint) 
    createObstacles()

    drone = obj("drone",11,11,8,"blue")        
    base = obj("base",2,3,2,"red")
    addKnownObject(drone)
    addKnownObject(base)
    action=""
    droneActions="Randomizing world"
     
     
seedWorld()

#check if object 1 and object 2 are next to each other on the x and y axis, disregards the z axis
def isNearXY(obj1,obj2):
    if (obj1.x==obj2.x or obj1.x+1==obj2.x or obj1.x-1==obj2.x):
        if (obj1.y==obj2.y or obj1.y+1==obj2.y or obj1.y-1==obj2.y):
          return True
    return False

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
            
            
            
        # auto pilot code
        if (action=="ap"):
             movementPerformed=False
             droneActions= ""
             xBlocked=False
             yBlocked=False
             zBlocked=False
             

             
             
             if (int(value1) < drone.x):
                if (safeToMove(drone.x - 1,drone.y,drone.z )==True):
                    currentMoveX = currentMoveX  - 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on x- axis"
                    xBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on x- axis"
                    xBlocked=True
                    
             if (int(value1) > drone.x):
                if (safeToMove(drone.x + 1,drone.y,drone.z )==True):
                    currentMoveX = currentMoveX + 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on x+ axis"
                    xBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on x+ axis"
                    xBlocked=True
                
             if (int(value2) > drone.y):
                if (safeToMove(drone.x ,drone.y + 1,drone.z )==True):
                    currentMoveY = currentMoveY + 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on y+ axis"
                    yBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on y+ axis"
                    yBlocked=True
                    
             if (int(value2) < drone.y):
                if (safeToMove(drone.x ,drone.y - 1,drone.z )==True):
                    currentMoveY = currentMoveY - 1
                    movementPerformed=True
                    droneActions= droneActions + ", Moving to destination on y- axis"
                    yBlocked=False
                else:
                    movementPerformed=False  
                    droneActions= droneActions + ", Avoiding collision on y- axis"
                    yBlocked=True
             
             # if drone is near destination
             if (isNearXY(drone,obj("dest",int(value1),int(value2),int(value3),""))==True):
                 
                 if (int(value3) < drone.z):
                    if (safeToMove(drone.x,drone.y,drone.z - 1)==True):
                        droneActions= droneActions + ", Lowering drone to z- destination"
                        movementPerformed=True
                        currentMoveZ = currentMoveZ - 1
                        zBlocked=False
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding collision on z- axis"
                        zBlocked=True
                        
                 if (int(value3) > drone.z):
                    if (safeToMove(drone.x,drone.y,drone.z + 1)==True):
                        droneActions= droneActions + ", Raising drone to z+ destination"
                        movementPerformed=True
                        currentMoveZ = currentMoveZ + 1
                    else:
                        movementPerformed=False  
                        droneActions= droneActions + ", Avoiding +collision on z+ axis"
                        zBlocked=True
             else:
                if (drone.z < defaultFlightHeight):
                    if (safeToMove(drone.x,drone.y,drone.z + 1)==True):
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
                        if (safeToMove(drone.x,drone.y,drone.z + 1)==True):
                            droneActions= droneActions + ", Raising drone z+ to avoid obstacle"
                            movementPerformed=True
                            currentMoveZ =  1
                        else:
                            droneActions= droneActions + ", Drone unable to fly over obstacle"
                            if (safeToMove(drone.x + 1,drone.y,drone.z )==True):
                                droneActions= droneActions + ", x+ axis attempt to avoid collision at max height"
                                movementPerformed=True
                                currentMoveX = 1
                            else:
                                if (safeToMove(drone.x - 1,drone.y,drone.z )==True):
                                    droneActions= droneActions + ", x- axis attempt to avoid collision at max height"
                                    movementPerformed=True
                                    currentMoveX = -1
                                else:
                                    droneActions= droneActions + ", Unable to use x axis to avoid obstacle"
                                    if (safeToMove(drone.x,drone.y + 1,drone.z)==True):
                                        droneActions= droneActions + ", y+ axis attempt to avoid collision at max height"
                                        movementPerformed=True
                                        currentMoveY =  1
                                    else:
                                        if (safeToMove(drone.x,drone.y-1,drone.z)==True):
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
        
        drone.x=drone.x + currentMoveX
        drone.y=drone.y + currentMoveY
        drone.z=drone.z + currentMoveZ
        
        knownObjs.pop(0)
        knownObjs.insert(0,drone)

        response_content = renderScripts(self) + renderWorld(self) 
                 
        #response_content = "<html><body><h1>Hello, World!</h1></body></html>"
        self.wfile.write(response_content.encode())

def run(server_class=HTTPServer, handler_class=webRequestHandler, port=8001):
   server_address = ('', port)
   httpd = server_class(server_address, handler_class)
   print(f"Starting server on port {port}...")
   httpd.serve_forever()
  
if __name__ == '__main__':
   run()