#check if object 1 and object 2 are next to each other on the x and y axis, disregards the z axis
def isNearXY(obj1,obj2):
    
    if (obj1.x==obj2.x or obj1.x+1==obj2.x or obj1.x-1==obj2.x):
        if (obj1.y==obj2.y or obj1.y+1==obj2.y or obj1.y-1==obj2.y):
          return True
    return False


def safeToMove(x,y,z,maxFlightHeight,knownObjs):
    if (z> maxFlightHeight):
        return False
    
    for objs in knownObjs:
        if (objs.name!="drone"):
            if (x >= objs.x1() and x <= objs.x2()):
                if (y >= objs.y1() and y <= objs.y2()):
                    if (z >= objs.z1() and z <= objs.z2()):
                        print("Near collision with " + objs.getLabel())
                        return False
    return True


def safeToMoveOld(x,y,z,maxFlightHeight,knownObjs):
    if (z> maxFlightHeight):
        return False
    for objs in knownObjs:
        if (objs.name!="drone"):
            if (objs.x==x and objs.y==y and objs.z==z):
                print("Near collision with " + objs.getLabel())
                return False
    return True