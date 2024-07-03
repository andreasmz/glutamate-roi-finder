import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.signal import convolve2d

img = np.zeros((10,5,5))
for i in range(10):
    n = np.full((5,5), i+1)
    img[i] = n

def ConvCorr(
        img: np.ndarray,
        radius: int 
    ):
    print("Halt")
    return
    mask = CircleMask(radius)
    #plt.imshow(mask)
    #plt.show()
    conv = np.zeros(img.shape)
    for i in range(img.shape[0]):
        conv[i] = convolve2d(img[i], mask, mode="same", boundary="symm")
        print(i)
    return conv


def CircleMask(radius: int) -> np.ndarray:
    x = np.arange(-radius, +radius+1)
    y = np.arange(-radius, +radius+1)
    mask = np.array((x[np.newaxis,:])**2 + (y[:,np.newaxis])**2 <= radius**2, dtype="int32")
    n = np.count_nonzero(mask==1)
    return mask/n

m = CircleMask(6)
for i in range(m.shape[0]):
    s = ""
    for n in range(m.shape[1]):
        s += str(round(m[i,n],3))
        s += " "
    print(s)