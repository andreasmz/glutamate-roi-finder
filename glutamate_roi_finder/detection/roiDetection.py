import skimage as ski
import numpy as np
import math

labeledImg = None
regProps = None
rois = None

def Label(img, radius, minROISize):
    global labeledImg, regProps, rois
    labeledImg = ski.measure.label(img, connectivity=2)
    regProps = ski.measure.regionprops(labeledImg)
    rois = []
    for i in range(len(regProps)):
        if(regProps[i].area >= math.pi*(radius**2)*minROISize):
            rois.append((int(round(regProps[i].centroid[1],0)), int(round(regProps[i].centroid[0],0))))
