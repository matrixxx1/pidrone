#check if object 1 and object 2 are next to each other on the x and y axis, disregards the z axis
def isNearXY(obj1,obj2):
    
    if (obj1.x==obj2.x or obj1.x+1==obj2.x or obj1.x-1==obj2.x):
        if (obj1.y==obj2.y or obj1.y+1==obj2.y or obj1.y-1==obj2.y):
          return True
    return False

def distanceBetweenObjects(obj1,obj2):
    
        print("distanceBetweenObjects-obj1 " + obj1.getLabel())
        print("distanceBetweenObjects-obj2 " + obj2.getLabel())
    
        distanceToDest=0
        
        if not isinstance(obj1.x, int):
            raise TypeError("obj1.x must be an object, instead its " + x)

        if not isinstance(obj2.x, int):
            raise TypeError("obj2.x must be an object, instead its " + x)

        if (obj2.x > obj1.x):
            distanceToDest=distanceToDest + obj2.x - obj1.x
        else:
            distanceToDest=distanceToDest + obj1.x - obj2.x
            
        if (obj2.y > obj1.y):
            distanceToDest=distanceToDest + obj2.y - obj1.y
        else:
            distanceToDest=distanceToDest + obj1.y - obj2.y
            
        if (obj2.z > obj1.z):
            distanceToDest=distanceToDest + obj2.z - obj1.z
        else:
            distanceToDest=distanceToDest + obj1.z - obj2.z
        
        print("distanceBetweenObjects-distanceToDest " + str(distanceToDest))
        
        return distanceToDest

#check if a coordinate is safe to move to, if it is, it returns None. If not safe, it returns the object
def getObjectByCoordinate(x,y,z,knownObjs):
    
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