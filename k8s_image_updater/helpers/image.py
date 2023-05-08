import re

class Image:
    def __init__(self, image):
        if re.match('.*/.*:.*', image):
            image = re.split('/|:', image)
            self.registry = image[0]
            self.imagename = '/'.join(image[1:-1])
            self.tag = image[-1]
        else:
            raise Exception("Not a valid image name")
        
    
    def print(self):
        print(f"Registry: {self.registry}, Imagename: {self.imagename}, Tag: {self.tag}")