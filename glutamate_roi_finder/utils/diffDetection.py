import numpy as np
from scipy.ndimage import convolve
import threading

global img,imgDiff,imgDiffMax,imgDiffRegions,imgConv
img = None
imgDiff = None
imgDiffMax = None
imgDiffRegions = None
imgConv = None

def ProcessImg():
    global img, imgDiff, imgDiffMax
    if img is None:
        return
    imgDiff = np.diff(img, axis=0)
    imgDiffMax = np.max(imgDiff,axis=0)

def Diff_Mask(threshold):
    global imgDiffMax, imgDiffRegions
    if imgDiffMax is None:
        return
    imgDiffRegions = (imgDiffMax >= threshold).astype(int)


def ConvCorr(
        img: np.ndarray,
        radius: int 
    ) -> np.ndarray:
    mask, n = CircleMask(radius)
    mask3 = mask[np.newaxis, :]
    return convolve(img,mask3)/n


def CircleMask(radius: int) -> (np.ndarray, int):
    x = np.arange(-radius, +radius+1)
    y = np.arange(-radius, +radius+1)
    mask = np.array((x[np.newaxis,:])**2 + (y[:,np.newaxis])**2 <= radius**2, dtype="int32")
    n = np.count_nonzero(mask==1)
    return (mask,n)

def _ConvTask(img, radius):
    global imgConv
    imgConv = ConvCorr(img, radius)
    print("Convolution calculated")

def ConvTask():
    t1 = threading.Thread(target=_ConvTask, args=(img,6))
    t1.start()