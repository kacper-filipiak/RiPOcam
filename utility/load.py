import cv2
import numpy as np

def load_image(path):
    return cv2.imread(path)

def load_video(path):
    cap = cv2.VideoCapture(path)
    if (cap.isOpened() == False):
        print("Error opening video file")

    # Read until video is completed
    while(cap.isOpened()):

    # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            yield frame
        else:
            break
    cap.release()
