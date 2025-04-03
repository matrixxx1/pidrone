import http
from http.server import BaseHTTPRequestHandler, HTTPServer

class object():
    def __init__(self, name, x, y,z, color):
        self.name=name
        self.x = x
        self.y = y
        self.z= z
        self.color=color

#worldx = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#worldy = [worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx,worldx]
#worldz = [worldy,worldy,worldy,worldy,worldy,worldy,worldy,worldy,worldy]
   
theWorld = []

for y in range(30):
    for x in range(20):
        for z in range(8):
            worldPoint = object("",x,y,8 - z,"")
            theWorld.append(worldPoint)
           
            
drone = object("drone",11,11,8,"blue")        
base = object("base",2,2,2,"blue")


knownObjects= []

knownObjects.append(drone)
knownObjects.append(base)

for y in range(30):
    for x in range(20):
        worldPoint = object("ground",x,y,1,"green")
        knownObjects.append(worldPoint)  


for x in range(8):
    obstacle = object("base",5,5,x,"black")
    knownObjects.append(obstacle)
    obstacle = object("base",15,15,x,"black")
    knownObjects.append(obstacle)
    obstacle = object("base",10,10,x,"black")
    knownObjects.append(obstacle)


  
class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        blocksize = 25
        response_content = "<BR>Map:<BR><BR><BR><BR><BR><BR><BR>"
        #response_content = response_content + "<style> .mtile {  opacity: 0.5;    transform: rotate3d(1,1, 0,45deg); position: absolute; top: 150 ; left: 150; } </style>"
        #response_content = response_content + "<style> .mrow {  } </style>"
        response_content = response_content + "<style> .mcell {  opacity: 0.8; transform: rotate3d(1,0, 0,35deg);  border: 1px dotted red; width: " + str(blocksize) + "px; height: " + str(blocksize) + "px;} </style>"
        #zcounter = 0
        #ycounter = 0
        #xcounter =0
        
        for pt in theWorld:
            response_content = response_content + "<div class='mcell' style='position: absolute; "
            response_content = response_content + " top: " + str((pt.x * blocksize) - (pt.z * 5) + 150) + "; "
            response_content = response_content + " left: " + str((pt.y  * blocksize) - (pt.z * 5) + 150) + "; "
            response_content = response_content + " z-index: -" + str(pt.z) + "; "
            objFound = False
            for objs in knownObjects:
                if (objs.x==pt.x and objs.y==pt.y and objs.z==pt.z):
                    response_content = response_content + "  background-color: " + objs.color + "; "
                    objFound=True
            
            response_content = response_content + "'></div>" 
        #response_content = "<html><body><h1>Hello, World!</h1></body></html>"
        self.wfile.write(response_content.encode())

def run(server_class=HTTPServer, handler_class=CustomHandler, port=8001):
   server_address = ('', port)
   httpd = server_class(server_address, handler_class)
   print(f"Starting server on port {port}...")
   httpd.serve_forever()
  
if __name__ == '__main__':
   run()