import tkinter as tk
from tkinter import ttk
import imagej
import threading
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import detection.diffDetection as detectDiff


def GUI():
    def StartImageJ():
        global ij, ij_load
        path1 = "C:\\Users\\abril\\Desktop\\Arbeitsprogramme\\fiji-win64\\Fiji.app"
        path2 = "C:\\Users\\abril\\Andreas Eigene Dateien\\Programme\\Fiji.app"

        ij = imagej.init(path1, mode='interactive')
        ij.ui().showUI()
        menuImageJ.entryconfig("Read Image", state="normal")
        progStartingImgJ.pack_forget()
        lblStartImageJ.pack_forget()

        lblImgInfo["text"] = "No image selected"
        lblImgInfo.pack()
        ij_load = None

    def MbtnStartImageJ_Click():
        global ij_load
        lblStartImageJ.pack()
        ij_load = True

        menuImageJ.entryconfig("Start ImageJ", state="disabled")

        def ProgStartingImgJ_Step():
            progStartingImgJ.step(10)
            if ij_load is not None:
                root.after(50, ProgStartingImgJ_Step)
        progStartingImgJ.pack()
        ProgStartingImgJ_Step()
        
        t = threading.Thread(target=StartImageJ)
        t.start()
    
    def MBtnReadImage():
        detectDiff.img = ij.py.active_xarray() 
        if detectDiff.img is None:
            return
        detectDiff.img = np.array(detectDiff.img)
        if (np.max(detectDiff.img) <= 2**15):
            detectDiff.img = detectDiff.img.astype("int16")
        if detectDiff.img is not None:
            lblImgInfo["text"] = f"{detectDiff.img.shape}, dtype={detectDiff.img.dtype}"
            detectDiff.ProcessImg()
            detectDiff.ProcessDiff()
            Replot()
        else:
            lblImgInfo["text"] = "No image selected"

    def Replot():
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        if detectDiff.img is None or detectDiff.imgDiffMax is None:
            return
        
        ax1.imshow(detectDiff.imgDiffMax)

        X = np.arange(0,detectDiff.imgDiffMax.shape[0])
        Y = np.arange(0,detectDiff.imgDiffMax.shape[1])
        X, Y = np.meshgrid(X, Y)
        #C = (detectDiff.imgDiffMax > scaleDiff.get()).astype(int)
        #lblDebug = str(C)
        ax2.plot_surface(X,Y, detectDiff.imgDiffMax)

        ax3.imshow((detectDiff.imgDiffMax >= scaleDiff.get()).astype(int))

        canvas.draw()
    
    def ScaleDiff_ValueChanged(val):
        Replot()

    root = tk.Tk()
    root.title("Glutamte Image ROI Detector")

    toolFrame = tk.Frame(root)
    toolFrame.pack(side=tk.LEFT, fill="both", expand=False)

    plotFrame = tk.Frame(root)
    plotFrame.pack(expand=True, fill="both")

    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menuImageJ = tk.Menu(menubar,tearoff=0)
    menubar.add_cascade(label="ImageJ",menu=menuImageJ)

    menuImageJ.add_command(label="Start ImageJ", command=MbtnStartImageJ_Click)
    menuImageJ.add_command(label="Read Image",state="disabled", command=MBtnReadImage)
    menuImageJ.add_command(label="Test",state="normal", command=Replot)

    progStartingImgJ = ttk.Progressbar(toolFrame,orient="horizontal", mode="indeterminate", length=200)
    lblStartImageJ = tk.Label(toolFrame,text="Starting ImageJ...")
    lblImgInfo = tk.Label(toolFrame)

    lblDebug = tk.Label(toolFrame)
    lblDebug.pack()

    scaleDiff = tk.Scale(toolFrame, from_=1, to=200, orient="horizontal", command=ScaleDiff_ValueChanged)
    scaleDiff.pack(fill="x")

    figure = plt.Figure(figsize=(6,6), dpi=100)
    ax1 = figure.add_subplot(221)  
    ax2 = figure.add_subplot(222,projection="3d") 
    ax3 = figure.add_subplot(223)  
    ax4 = figure.add_subplot(224) 
    ax1.set_title("Diff Maximum")
    ax2.set_title("Diff 3D Projection")
    ax3.set_title("Detected Neuron areas")
    ax4.set_title("ROIs")
    canvas = FigureCanvasTkAgg(figure, plotFrame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    root.mainloop()