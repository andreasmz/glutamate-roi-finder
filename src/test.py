import tkinter as tk
import imagej_handler as ij
import numpy as np
from xarray.core.dataarray import DataArray

def Loop():
    img = None
    ij.Init()
    ij.Show()

    def Button1_Click():
        print("Click")
        img: DataArray = ij.ij.py.active_xarray() 

        print(img.dims)
        '''
        <xarray.DataArray array([[[112, 115, 116, ..., 114, 116, 115],
            [ 92, 126, 109, ..., 109, 115, 115],
            [113,  97, 109, ..., 106, 102, 112],
            ...,
            [108, 127, 100, ..., 109, 109, 114],
            [107, 106, 135, ..., 109, 107, 108],
            [114, 107, 117, ..., 111, 102, 112]],
            Coordinates:
            * t        (t) float64 4kB 0.0 0.01001 0.02002 0.03002 ... 4.484 4.494 4.504
            * row      (row) float64 6kB 0.0 0.072 0.144 0.216 ... 57.31 57.38 57.46 57.53
            * col      (col) float64 6kB 0.0 0.072 0.144 0.216 ... 57.31 57.38 57.46 57.53
        '''
        ij.ij.py.show(img[0, :])

    tmain = tk.Tk()

    btn1 = tk.Button(tmain, text="Button 1", justify="center", command=Button1_Click)
    btn1.pack(padx=20,pady=20)

    tmain.mainloop()
