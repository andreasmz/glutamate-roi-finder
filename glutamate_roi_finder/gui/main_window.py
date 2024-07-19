import gui.settings as settings

import os, sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import imagej
import threading
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle

import detection.diffDetection as detectDiff


def GUI():
    def ImageJReady():
        menuImageJ.entryconfig("Read Image", state="normal")
        menuImageJ.entryconfig("Save dump", state="normal")

    def StartImageJ():
        global ij, ij_load
        ij = imagej.init(settings.ImageJPath, mode='interactive')
        ij.ui().showUI()
        ImageJReady()
        progStartingImgJ.grid_forget()
        lblStartImageJ.grid_forget()

        lblImgInfo["text"] = "No image selected"
        lblImgInfo.grid(row=2, column=0, columnspan=2)
        ij_load = None

    def MbtnStartImageJ_Click():
        global ij_load
        if (settings.ImageJPath is None):
            return
        if (not os.path.exists(settings.ImageJPath)):
            messagebox.showerror("Glutamate Roi Finder", "The given ImageJ path doesn't exist")
            return

        lblStartImageJ.grid(row=1, column=0)
        ij_load = True

        menuImageJ.entryconfig("Start ImageJ", state="disabled")

        def ProgStartingImgJ_Step():
            progStartingImgJ.step(10)
            if ij_load is not None:
                root.after(50, ProgStartingImgJ_Step)
        progStartingImgJ.grid(row=1, column=1)
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
            print("Img Size =", sys.getsizeof(detectDiff.imgDiffMax))
        else:
            lblImgInfo["text"] = "No image selected"

    def Replot():
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        if detectDiff.imgDiffMax is None:
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

    def intDiff_ValueChanged():
        Replot()

    def _Debug_Save():
        savePath = os.path.join(settings.parentPath, "imgDiffMax.dump")
        print("Saved dump to", savePath)
        with open(savePath, 'wb') as outp:
            pickle.dump(detectDiff.imgDiffMax, outp, pickle.HIGHEST_PROTOCOL)

    def _Debug_Load():
        savePath = os.path.join(settings.parentPath, "imgDiffMax.dump")
        with open(savePath, 'rb') as intp:
            detectDiff.imgDiffMax = pickle.load(intp)
        ImageJReady()
        lblImgInfo["text"] = "Img from dump"
        Replot()

    root = tk.Tk()
    root.title("Glutamte Image ROI Detector")

    if (settings.ImageJPath is None):
        messagebox.showerror("Glutamate Roi Finder", "The settings.json couldn't be read")
        exit()

    toolFrame = tk.Frame(root)
    toolFrame.pack(side=tk.LEFT, fill="both", expand=False)

    plotFrame = tk.Frame(root)
    plotFrame.pack(side=tk.RIGHT, fill="both", expand=True)

    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menuImageJ = tk.Menu(menubar,tearoff=0)
    menubar.add_cascade(label="ImageJ",menu=menuImageJ)

    menuImageJ.add_command(label="Start ImageJ", command=MbtnStartImageJ_Click)
    menuImageJ.add_command(label="Read Image",state="disabled", command=MBtnReadImage)
    menuImageJ.add_command(label="Save dump",state="disabled", command=_Debug_Save)
    menuImageJ.add_command(label="Load dump",state="normal", command=_Debug_Load)

    progStartingImgJ = ttk.Progressbar(toolFrame,orient="horizontal", mode="indeterminate", length=200)
    lblStartImageJ = tk.Label(toolFrame,text="Starting ImageJ...")
    lblImgInfo = tk.Label(toolFrame)

    #lblToolFrame = tk.Label(toolFrame, text="", width=32)
    #lblToolFrame.grid(row=1, column=0)
    lblScaleDiffInfo = tk.Label(toolFrame, text="Threshold for diff detection")
    lblScaleDiffInfo.grid(row=3, column=0, columnspan=2)
    varDiff = tk.IntVar(value=20)
    intDiff = tk.Spinbox(toolFrame, from_=1, to=200, textvariable=varDiff,width=5, command=intDiff_ValueChanged)
    intDiff.grid(row=4, column=0)
    scaleDiff = tk.Scale(toolFrame, variable=varDiff, from_=1, to=200, orient="horizontal", command=ScaleDiff_ValueChanged, showvalue=False)
    scaleDiff.grid(row=4, column=1)

    lblDebug = tk.Label(toolFrame)
    lblDebug.grid(row=5, column=0, columnspan=2)

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