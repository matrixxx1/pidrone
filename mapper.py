import http
from http.server import BaseHTTPRequestHandler, HTTPServer

import urllib.parse


blocksize = 15
padtop= 50
padleft=50
heightpad = blocksize / 2
leftpad = blocksize      /2   
       
       
worldX=60
worldY=20
worldZ=10
       
class object():
    def __init__(self, name, x, y,z, color):
        self.name=name
        self.x = x
        self.y = y
        self.z= z
        self.color=color

    def renderIt(self):
        top = (self.x * blocksize)   + padtop - (self.z * heightpad) 
        left = (self.y  * blocksize)  + padleft - (self.z  * leftpad)
        retval = ""
        retval = retval + "<div  style='position: absolute; top: " + str(top+6) + ";   left: " + str(left +6) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " background-color: " + self.color + ";'   class='mcellsha'></div>"
        retval = retval + "<div  style='position: absolute; top: " + str(top+3) + ";   left: " + str(left +3) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " background-color: " + self.color + ";'   class='mcellsha'></div>" 
        retval = retval + "<div onclick='setDest(" + str(self.x) + "," + str(self.y) +  "," + str(self.z) + ")' title='name: " + self.name + ", x: " + str(self.x) +", y: " + str(self.y) + ", z: " + str(self.z) + "'  style='position: absolute; top: " + str(top) + ";   left: " + str(left) + ";  z-index: " + str(self.z) + ";  "
        retval = retval  + " background-color: " + self.color + ";'   class='mcellobj'></div>" 

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

for x in range(3):
    for y in range(10):
        knownObjects.append(object("tree",5,y,x+1,"black"))
        knownObjects.append(object("tree",15,y,x+1,"black"))
        knownObjects.append(object("tree",10,y,x+1,"black"))


def renderWorld():
    response_content = "<BR>Drone coords: x: " + str(drone.x) +", y: " + str(drone.y) + ", z: " + str(drone.z) + "  <BR><BR><BR><BR><BR><BR><BR>"
    response_content = response_content + " <a href='/?action=move&value=left'><</a> | <a href='/?action=move&value=right'>></a> | "
    response_content = response_content + " <a href='/?action=move&value=up'>/\</a> | <a href='/?action=move&value=down'>\/</a> | "
    response_content = response_content + "<a href='/?action=move&value=higher'>H</a> | <a href='/?action=move&value=lower'>L</a> <BR><BR><BR><BR><BR><BR><BR>"
    response_content = response_content + "<style> .mcell {  border: 1px dashed yellow; opacity: 0.8; transform-style: preserve-3d; transform: translateY(-10px) rotateX(65deg);   width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "<style> .mcellobj {      border: 1px dashed red;  width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    response_content = response_content + "<style> .mcellsha {      border-bottom: 2px solid black; border-right: 2px solid black;  width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
    
    response_content = response_content + "<script> function setDest(x,y,z){ window.location.href='/?action=ap&value=' + x + '&value2=' + y + '&value3=' + z; } </script>"
    
    top=0
    left = 0
    classes = ""        
    for checkz in range(worldZ):
        z = worldZ - checkz
        response_content = response_content + "<div class='.mcell' style='position: absolute; width: " + str(worldX * blocksize) + "px;  height: " + str(worldY * blocksize) + "px'>"
        for objs in knownObjects:
            if (objs.z==z):
                response_content = response_content + objs.renderIt() 
        response_content = response_content + "</div>"
    return response_content
  
class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
        
        if (action=="ap"):
             actiondone=False
             if (int(value1) < drone.x and actiondone==False):
                actiondone=True
                drone.x=drone.x - 1  
             if (int(value1) > drone.x and actiondone==False):
                actiondone=True
                drone.x=drone.x + 1
                
             if (int(value2) > drone.y and actiondone==False):
                actiondone=True
                drone.y=drone.y + 1
             if (int(value2) < drone.y and actiondone==False):
                actiondone=True
                drone.y=drone.y - 1
                
             if (int(value3) < drone.z and actiondone==False):
                actiondone=True
                drone.z=drone.z - 1 
             if (int(value3) > drone.z and actiondone==False):
                actiondone=True
                drone.z=drone.z + 1
              
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

        response_content = renderWorld()
                 
        #response_content = "<html><body><h1>Hello, World!</h1></body></html>"
        self.wfile.write(response_content.encode())

def run(server_class=HTTPServer, handler_class=CustomHandler, port=8001):
   server_address = ('', port)
   httpd = server_class(server_address, handler_class)
   print(f"Starting server on port {port}...")
   httpd.serve_forever()
  
if __name__ == '__main__':
   run()