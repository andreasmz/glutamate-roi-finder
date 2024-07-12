import numpy as np

img = None

def ProcessImg():
    global imgDiff, imgDiffMax
    if img is None:
        return
    imgDiff = np.diff(img, axis=0)
    imgDiffMax = np.max(imgDiff,axis=0)

def ProcessDiff():
    global imgDiff, imgDiffMax
    if imgDiff is None or imgDiffMax is None:
        return