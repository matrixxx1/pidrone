import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# to install on windows
# pip install matplotlib
# if pip isnt working -  setx PATH "%PATH%;c:\program files (x86)\microsoft visual studio\shared\python39_64\Scripts"
# c:\program files (x86)\microsoft visual studio\shared\python39_64\Scripts

class Object3D:
    def __init__(self, name, x, y, z, isGround):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.isGround= isGround

    def move(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz

    def get_position(self):
        return (self.x, self.y, self.z)

    def to_dict(self):
        return {"name": self.name, "x": self.x, "y": self.y, "z": self.z, "isGround": self.isGround}

class ObjectTracker:
    def __init__(self):
        self.objects = {}

    def add_object(self, name, x, y, z, isGround):
        self.objects[name] = Object3D(name, x, y, z, isGround)

    def move_object(self, name, dx, dy, dz):
        if name in self.objects:
            self.objects[name].move(dx, dy, dz)

    def get_positions(self):
        return {name: obj.get_position() for name, obj in self.objects.items()}

    def render_objects(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        for name, obj in self.objects.items():
            x, y, z = obj.get_position()
            if obj.isGround==True:
                ax.scatter(x, y, z, label="")
            else:
                ax.scatter(x, y, z, label=name)
                
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
        ax.set_zlabel("Z Axis")
        ax.legend()
        plt.show()

# Example Usage
tracker = ObjectTracker()
tracker.add_object("Base", 1, 2, 1, False)
tracker.add_object("Drone1", 5, 5, 5,False)
tracker.add_object("Drone2", 5, 5, 4,False)
#tracker.move_object("Drone", 1, -1, 0)

for x in range(30):  # Generates numbers from 0 to 4
    for y in range(30):  # Generates numbers from 0 to 4
         tracker.add_object("Ground-" + str(x) + str(y), x, y, 0, True) 

#tracker.add_object("Ground1", 1, 1, 1) 
#tracker.add_object("Ground2", 1, 2, 1)
#tracker.add_object("Ground3", 1, 1, 2) 

# Render the objects in 3D
tracker.render_objects()
