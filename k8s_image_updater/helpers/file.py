from pathlib import Path
from .image import Image

class File:
    def __init__(self, path: Path):
        self.path = path
        self.images = []


    def addImage(self, image: Image):
        self.images.append(image)


    def printImages(self):
        for image in self.images:
            print(f"Registry: {image.registry}, Imagename: {image.imagename}, Tag: {image.tag}")