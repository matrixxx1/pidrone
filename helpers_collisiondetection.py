#check if object 1 and object 2 are next to each other on the x and y axis, disregards the z axis
def isNearXY(obj1,obj2):
    x_diff = abs(obj1.x - obj2.x)
    y_diff = abs(obj1.y - obj2.y)
    return x_diff <= 1 and y_diff <= 1




class spacialCoordinate():
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
    
    def __init__(self, name, x, y,z, objHeight=1, objWidth=1, objDepth=1):
        if not isinstance(x, int):
            raise TypeError("x must be an integer, instead its " + x)
        if not isinstance(y, int):
            raise TypeError("y must be an integer, instead its " + y)
        if not isinstance(z, int):
            raise TypeError("z must be an integer, instead its " + z)
        if not isinstance(objHeight, int):
            raise TypeError("objHeight must be an integer, instead its " + objHeight)
        if not isinstance(objWidth, int):
            raise TypeError("objWidth must be an integer, instead its " + objWidth)
        if not isinstance(objDepth, int):
            raise TypeError("objDepth must be an integer, instead its " + objDepth)
        self.name=name
        self.x = x
        self.y = y
        self.z= z
        self.height=objHeight
        self.width=objWidth
        self.depth=objDepth
        self.id=0
        self.note=""
        
    def getLabel(self):
        retval = self.name + " coords: [" + str(self.x) +"," + str(self.y) + "," + str(self.z) + "]"
        if (self.width>1 or self.height > 1 or self.depth > 1):
            retval = retval + ", size: [" + str(self.width) +"," + str(self.height) + "," + str(self.depth)  + "]"
        if (self.id > 0):
            retval = retval +" , id: " + str(self.id)
        if len(self.note) > 0:
            retval = retval +" , note: " + str(self.note)
        
        return retval
  

    



def distanceBetweenObjects(obj1,obj2):
    return abs(obj2.x - obj1.x) + abs(obj2.y - obj1.y) + abs(obj2.z - obj1.z)

#check if a coordinate is safe to move to, if it is, it returns None. If not safe, it returns the object
def getObjectByCoordinate(x, y, z, knownObjs):
    for obj in knownObjs:
        if obj.name not in {"drone", "apdestination"}:
            x1, x2 = obj.x1(), obj.x2()
            y1, y2 = obj.y1(), obj.y2()
            z1, z2 = obj.z1(), obj.z2()

            if x1 <= x <= x2 and y1 <= y <= y2 and z2 <= z <= z1:
                return obj
    return None


def getObjectByCoordinateOLD(x,y,z,knownObjs):
    
    for objs in knownObjs:
        if (objs.name!="drone" and objs.name!="apdestination"):
            if (x >= objs.x1() and x <= objs.x2()):
                #print("x axis " + str(x) + "  is between " + str(objs.x1()) + " and " + str(objs.x2()))
                if (y >= objs.y1() and y <= objs.y2()):
                    #print("y axis " +  str(y) + "  is between " + str(objs.y1()) + " and " + str(objs.y2()))
                    if (z <= objs.z1() and z >= objs.z2()):                        
                        #print("z axis " +  str(z) + "  is between " + str(objs.z1()) + " and " + str(objs.z2()))
                        #print("getObjectByCoordinate - Near collision with " + objs.getLabel())
                        return objs
                    #else:
                     #   print("z axis " +  str(z) + "  is NOT between " + str(objs.z1()) + " and " + str(objs.z2()))
               # else:
                        #print("y axis " +  str(y) + "  is NOT between " + str(objs.y1()) + " and " + str(objs.y2()))
           # else:
                        #print("x axis " +  str(x) + "  is NOT between " + str(objs.x1()) + " and " + str(objs.x2()))
    return None


def safeToMoveOld(x,y,z,maxFlightHeight,knownObjs):
    if (z> maxFlightHeight):
        return False
    for objs in knownObjs:
        if (objs.name!="drone"):
            if (objs.x==x and objs.y==y and objs.z==z):
                print("Drone [ x: " + str(x) + ", y:" + str(y) + ", z:" + str(z) + " ] Near collision with " + objs.getLabel())
                return False
    return True