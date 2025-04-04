import http
from http.server import BaseHTTPRequestHandler, HTTPServer

import urllib.parse


blocksize = 15
padtop= 70
padleft=70
heightpad = blocksize / 2
leftpad = blocksize      /2   
       
      
defaultFlightHeight = 10
      
worldX=60
worldY=30
worldZ=15
     
     
     
longTermGoalAchieved=False
droneActions=""

class object():
    def __init__(self, name, x, y,z, color):
        self.name=name
        self.x = x
        self.y = y
        self.z= z
        self.color=color
        
    def getLabel(self):
        return self.name + " coords: x: " + str(self.x) +", y: " + str(self.y) + ", z: " + str(self.z)

    def renderIt(self):
        top = (self.x * blocksize)   + padtop - (self.z * heightpad) 
        left = (self.y  * blocksize)  + padleft - (self.z  * leftpad)
        retval = ""
        retval = retval + "\n<div  style='position: absolute; top: " + str(top+6) + ";   left: " + str(left +6) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " background-color: " + self.color + ";'   class='mcellsha'></div>\n"
        retval = retval + "\n<div  style='position: absolute; top: " + str(top+3) + ";   left: " + str(left +3) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " background-color: " + self.color + ";'   class='mcellsha'></div>\n" 
        retval = retval + "\n <div onclick='setDest(" + str(self.x) + "," + str(self.y) +  "," + str(self.z + 1) + ")' "
        retval = retval + "\n title='name: " + self.name + ", x: " + str(self.x) +", y: " + str(self.y) + ", z: " + str(self.z) + "' "
        retval = retval + "\n style='position: absolute; top: " + str(top) + ";   left: " + str(left) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " background-color: " + self.color + ";'   class='mcellobj'></div>\n" 

        return retval
    
#worldx = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#worldy = [worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx]
#worldz = [worldy,worldy,worldy,worldy,worldy,worldy,worldy,worldy,worldy]
   
theWorld = []

for y in range(worldX):
    for x in range(worldY):
        for z in range(worldZ):
            worldPoint = object("",x,y,worldZ - z,"")
            theWorld.append(worldPoint)
           
            
drone = object("drone",11,11,8,"blue")        
base = object("base",2,3,2,"red")


knownObjects= []

knownObjects.append(drone)
knownObjects.append(base)

for y in range(worldX):
    for x in range(worldY):
        worldPoint = object("ground",x,y,1,"green")
        knownObjects.append(worldPoint)  


        
for x in range(6):
    knownObjects.append(object("tree",5,5,x+1,"black"))
    knownObjects.append(object("tree",15,15,x+1,"black"))
    knownObjects.append(object("tree",10,10,x+1,"black"))


        
for x in range(6):
    knownObjects.append(object("tree",16,5,x+1,"black"))
    knownObjects.append(object("tree",25,15,x+1,"black"))
    knownObjects.append(object("tree",22,10,x+1,"black"))


for x in range(3):
    for y in range(10):
        knownObjects.append(object("tree",25,y,x+1,"black"))
        knownObjects.append(object("tree",15,x+y,x+1,"black"))
        knownObjects.append(object("tree",20,y,x+1,"black"))


for x in range(3):
    for y in range(10):
        knownObjects.append(object("tree",5,y,x+1,"black"))
        knownObjects.append(object("tree",15,y,x+1,"black"))
        knownObjects.append(object("tree",10,y,x+1,"black"))

def safeToMove(x,y,z):
    for objs in knownObjects:
        if (objs.name!="drone"):
            if (objs.x==x and objs.y==y and objs.z==z):
                print("Near collision with " + objs.getLabel())
                return False
    return True
    
def renderActions(self, droneActions,longTermGoalAchieved):
    parsed_path = urllib.parse.urlparse(self.path)
    query_string = parsed_path.query
         
    # Parse the query string into a dictionary
        
    query_params = urllib.parse.parse_qs(query_string)
        
    action = query_params.get('action',[''])[0]
    value1 = query_params.get('value',[''])[0]
    value2 = query_params.get('value2',[''])[0]
    value3 = query_params.get('value3',[''])[0]
    value4 = query_params.get('value4',[''])[0]
    value5 = query_params.get('value5',[''])[0]
    value6 = query_params.get('value6',[''])[0]
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
    retval = retval + "\n <a href='/?action=move&value=left'><</a> | <a href='/?action=move&value=right'>></a> | "
    retval = retval + "\n <a href='/?action=move&value=up'> /\\ </a> | <a href='/?action=move&value=down'>\\/</a> | "
    retval = retval + "\n<a href='/?action=move&value=higher'>H</a> | <a href='/?action=move&value=lower'>L</a> "
    retval = retval + "\n<BR><BR> Action: <input type='text' id='action' class='ip'  value='" + action + "'> \n"
    retval = retval + "\n Value1: <input type='text' id='value' class='ip' value='" + value1 + "'> "
    retval = retval + "\n Value2: <input type='text' id='value2' class='ip' value='" + value2 + "'> "
    retval = retval + "\n Value3: <input type='text' id='value3' class='ip' value='" + value3 + "'> "
    retval = retval + "\n Value4: <input type='text' id='value4' class='ip' value='" + value4 + "'> "
    retval = retval + "\n Value5: <input type='text' id='value5' class='ip' value='" + value5 + "'> "
    retval = retval + "\n Value6: <input type='text' id='value6' class='ip' value='" + value6 + "'> "
    retval = retval + "\n <input type='button' value='run' onclick='subForm();'>\n "
    return retval

def renderScripts(self):
    retval = "\n <script>  "
    retval = retval + "\n window.droneX=" + str(drone.x)
    retval = retval + "\n window.droneY=" + str(drone.y)
    retval = retval + "\n window.droneZ=" + str(drone.z)
    retval = retval + "\n function setDest(x,y,z){  window.location.href='/?action=ap&value=' + x + '&value2=' + y + '&value3=' + z  + '&value4=' + window.droneX  + '&value5=' + window.droneY  + '&value6=' + window.droneZ;}  \n"
    retval = retval + "\n function getIt(frmName){ return document.getElementById(frmName).value; }  \n"
    retval = retval + "\n function subForm(){ window.location.href='/?action=' + getIt(\"action\") + '&value=' + getIt(\"value\") + '&value2=' + getIt(\"value2\") + '&value3=' + getIt(\"value3\") + '&value4=' + getIt(\"value4\") + '&value5=' + getIt(\"value5\") + '&value6=' + getIt(\"value6\"); } \n"
    retval = retval + "\n function autoPilot(){ if (getIt(\"action\")!=\"\"){subForm();}} \n"
    retval = retval + "\n setTimeout(autoPilot, 2000); \n </script>"
    return retval

def renderWorld(self,droneActions,longTermGoalAchieved):
    #let timeoutId = setTimeout(greet, 2000, "World")
    response_content = "<BR>" + drone.getLabel() + "  " + renderActions(self,droneActions,longTermGoalAchieved)
    response_content = response_content + "\n<BR><BR><BR><BR><BR>\n"
    response_content = response_content + "\n<style> .mcell {  border: 1px dashed yellow; opacity: 0.8; transform-style: preserve-3d; transform: translateY(-10px) rotateX(65deg);   width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "\n<style> .mcellobj {      border: 1px dashed red;  width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "\n<style> .mcellsha {      border-bottom: 2px solid black; border-right: 2px solid black;  width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "\n<style> .ip {   width: 60px;   } </style>"

    
    
    top=0
    left = 0
    classes = ""        
    for checkz in range(worldZ):
        z = worldZ - checkz
        response_content = response_content + "\n<div class='.mcell' style='position: absolute; width: " + str(worldX * blocksize) + "px;  height: " + str(worldY * blocksize) + "px'>"
        for objs in knownObjects:
            if (objs.z==z):
                response_content = response_content + objs.renderIt() 
        response_content = response_content + "\n</div> "
    return response_content
  
class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        longTermGoalAchieved=False
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
         
        parsed_path = urllib.parse.urlparse(self.path)
        query_string = parsed_path.query
         
        # Parse the query string into a dictionary
        
        query_params = urllib.parse.parse_qs(query_string)
        
        action = query_params.get('action',[''])[0]
        value1 = query_params.get('value',[''])[0]
        value2 = query_params.get('value2',[''])[0]
        value3 = query_params.get('value3',[''])[0]
        value4 = query_params.get('value4',[''])[0]
        value5 = query_params.get('value5',[''])[0]
        value6 = query_params.get('value6',[''])[0]
        
        if (action=="ap"):
             actiondone=False

             if (int(value4) == drone.x and int(value5) == drone.y and  drone.z < defaultFlightHeight and actiondone==False):                
                if (safeToMove(drone.x,drone.y,drone.z + 1)==True):
                    drone.z=drone.z + 1
                    actiondone=True
                    droneActions="Gaining elevation to safe flight height"
                else:
                    actiondone=True  
                    droneActions="Avoiding collisionon z axis"
                
             if (int(value1) < drone.x and actiondone==False):
                if (safeToMove(drone.x - 1,drone.y,drone.z )==True):
                    drone.x=drone.x - 1
                    actiondone=True
                    droneActions="Moving to destination on x axis"
                else:
                    actiondone=True  
                    droneActions="Avoiding collisionon x axis"
                    
             if (int(value1) > drone.x and actiondone==False):
                if (safeToMove(drone.x + 1,drone.y,drone.z )==True):
                    drone.x=drone.x + 1
                    actiondone=True
                    droneActions="Moving to destination on x axis"
                else:
                    actiondone=True  
                    droneActions="Avoiding collisionon x axis"
                
             if (int(value2) > drone.y and actiondone==False):
                if (safeToMove(drone.x ,drone.y + 1,drone.z )==True):
                    drone.y=drone.y + 1
                    actiondone=True
                    droneActions="Moving to destination on y axis"
                else:
                    actiondone=True  
                    droneActions="Avoiding collisionon y axis"
                    
             if (int(value2) < drone.y and actiondone==False):
                if (safeToMove(drone.x ,drone.y - 1,drone.z )==True):
                    drone.y=drone.y - 1
                    actiondone=True
                    droneActions="Moving to destination on y axis"
                else:
                    actiondone=True  
                    droneActions="Avoiding collisionon y axis"
                
             if (int(value3) < drone.z and actiondone==False):
                droneActions="Lowering drone to destination"
                actiondone=True
                drone.z=drone.z - 1 
             if (int(value3) > drone.z and actiondone==False):
                droneActions="Raising drone to destination"
                actiondone=True
                drone.z=drone.z + 1
             if (int(value1) == drone.x and int(value2) == drone.y and int(value3) == drone.z and actiondone==False):
                droneActions="Drone has landed, autopilot complete"
                actiondone=True
                longTermGoalAchieved=True                
              
        if (action=="move"):
            if (value1=="higher"):
                drone.z=drone.z + 1
            if (value1=="lower"):
                drone.z=drone.z - 1                
            if (value1=="up"):
                drone.y=drone.y + 1          
            if (value1=="down"):
                drone.y=drone.y - 1          
            if (value1=="right"):
               drone.x=drone.x + 1          
            if (value1=="left"):
               drone.x=drone.x - 1
        
        knownObjects.pop(0)
        knownObjects.insert(0,drone)

        response_content = renderWorld(self,droneActions,longTermGoalAchieved) + renderScripts(self)
                 
        #response_content = "<html><body><h1>Hello, World!</h1></body></html>"
        self.wfile.write(response_content.encode())

def run(server_class=HTTPServer, handler_class=CustomHandler, port=8001):
   server_address = ('', port)
   httpd = server_class(server_address, handler_class)
   print(f"Starting server on port {port}...")
   httpd.serve_forever()
  
if __name__ == '__main__':
   run()