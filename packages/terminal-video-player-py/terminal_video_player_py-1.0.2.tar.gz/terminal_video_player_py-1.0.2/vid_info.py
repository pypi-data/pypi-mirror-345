import cv2
from PIL import Image

class vid_info:
    def __init__(self, file_name):
        self.vid = cv2.VideoCapture(file_name)

    def get_frame(self, frame_num):
        self.vid.set(1, frame_num)
        success,image = self.vid.read()
        if success:
            img = Image.fromarray(image)
            return img

    def get_framerate(self):

        return self.vid.get(cv2.CAP_PROP_FPS)

    def get_framecount(self):

        return self.vid.get(cv2.CAP_PROP_FRAME_COUNT)