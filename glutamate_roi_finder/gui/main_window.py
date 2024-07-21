import gui.settings as settings
import detection.diffDetection as detectDiff
import detection.roiDetection as roiDetect

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
from matplotlib.widgets import Slider
from matplotlib.patches import Circle
import pickle

from scyjava import jimport

def GUI():
    RM = None
    OvalRoi = None
    ij = None
    ij_load = None

    def ImageJReady():
        menuImageJ.entryconfig("Read Image", state="normal")
        menuImageJ.entryconfig("Save dump", state="normal")

    def StartImageJ():
        nonlocal ij, ij_load, RM, OvalRoi
        ij = imagej.init(settings.ImageJPath, mode='interactive')
        RM = jimport("ij.plugin.frame.RoiManager")
        OvalRoi = jimport('ij.gui.OvalRoi')
        ij.ui().showUI()
        ImageJReady()
        progStartingImgJ.pack_forget()
        lblStartImageJ.pack_forget()

        lblImgInfo["text"] = "No image selected"
        lblImgInfo.pack()
        ij_load = None

    def MbtnStartImageJ_Click():
        nonlocal ij_load
        if (settings.ImageJPath is None):
            return
        if (not os.path.exists(settings.ImageJPath)):
            messagebox.showerror("Glutamate Roi Finder", "The given ImageJ path doesn't exist")
            return

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
        nonlocal ij
        detectDiff.img = ij.py.active_xarray() 
        if detectDiff.img is None:
            return
        detectDiff.img = np.array(detectDiff.img)
        if (np.max(detectDiff.img) <= 2**15):
            detectDiff.img = detectDiff.img.astype("int16")
        if detectDiff.img is not None:
            detectDiff.imgConv = detectDiff.ConvTask()
            lblImgInfo["text"] = f"{detectDiff.img.shape}, dtype={detectDiff.img.dtype}"
            detectDiff.ProcessImg()
            Replot()
            print("Img Size =", sys.getsizeof(detectDiff.imgDiffMax))
        else:
            lblImgInfo["text"] = "No image selected"

    def Replot():
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        ax1.set_title("Diff Maximum")
        ax2.set_title("Diff 3D Projection")
        if detectDiff.imgDiffMax is None:
            return
        
        ax1.imshow(detectDiff.imgDiffMax)

        X = np.arange(0,detectDiff.imgDiffMax.shape[0])
        Y = np.arange(0,detectDiff.imgDiffMax.shape[1])
        X, Y = np.meshgrid(X, Y)
        #C = (detectDiff.imgDiffMax > scaleDiff.get()).astype(int)
        #lblDebug = str(C)
        ax2.plot_surface(X,Y, detectDiff.imgDiffMax)
        ReplotROI()

    def ReplotROI():
        ax3.clear()
        ax4.clear()
        ax3.set_title("Detected Neuron areas")

        if detectDiff.imgDiffMax is None:
            return

        detectDiff.Diff_Mask(scaleDiff.get())
        roiDetect.Label(detectDiff.imgDiffRegions, radius=varROIRadius.get(), minROISize=varROIMinSize.get()/100)

        selectedROI = None
        
        if (varROI.get() != 0 and varROI.get() <= len(roiDetect.rois)):
            roiCentroid = roiDetect.rois[varROI.get()-1]
            selectedROI = roiCentroid
            if (detectDiff.imgConv is not None):
                ax4.plot(detectDiff.imgConv[:, roiCentroid[0], roiCentroid[1]])
                ax4.set_title("ROI" + str(varROI.get()))

        ax3.imshow(detectDiff.imgDiffRegions)
        for roi in roiDetect.rois:
            color = "red" 
            if (selectedROI == roi):
                color = "yellow"
            c = Circle(roi, varROIRadius.get(), color=color, fill=False)
            ax3.add_patch(c)
        scaleROI.configure(to=len(roiDetect.rois))

        canvas.draw()

    def ExportROIs():
        nonlocal ij
        if ij is None:
            print("ij not started")
            return
        rm = RM.getRoiManager()
        for roi in roiDetect.rois:
            roi = OvalRoi(roi[0],roi[1], varROIRadius.get(), varROIRadius.get())
            rm.addRoi(roi)

    def ScaleDiff_Replot(val):
        Replot()

    def ScaleDiff_ReplotROI(val):
        ReplotROI()

    def intDiff_Replot():
        Replot()
    
    def intDiff_ReplotROI():
        ReplotROI()

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

    lblfDiffDetection = tk.LabelFrame(toolFrame, text="Diff detection")
    lblfDiffDetection.pack()
    lblScaleDiffInfo = tk.Label(lblfDiffDetection, text="threshold")
    lblScaleDiffInfo.grid(row=0, column=0, columnspan=2)
    varDiff = tk.IntVar(value=20)
    intDiff = tk.Spinbox(lblfDiffDetection, from_=1, to=200, textvariable=varDiff,width=5, command=intDiff_Replot)
    intDiff.grid(row=1, column=0)
    scaleDiff = tk.Scale(lblfDiffDetection, variable=varDiff, from_=1, to=200, orient="horizontal", command=ScaleDiff_Replot, showvalue=False)
    scaleDiff.grid(row=1, column=1)

    lblfRoiDetection = tk.LabelFrame(toolFrame, text="ROI Detection")
    lblfRoiDetection.pack()
    tk.Label(lblfRoiDetection, text="ROI radius").grid(row=0, column=0)
    varROIRadius = tk.IntVar(value=10)
    intROIRadius = tk.Spinbox(lblfRoiDetection, from_=1, to=25, textvariable=varROIRadius, width=5, command=intDiff_ReplotROI)
    intROIRadius.grid(row=0, column=1)
    tk.Label(lblfRoiDetection, text="px").grid(row=0, column=2)
    lblROIMinSize = tk.Label(lblfRoiDetection, text="Minimum size of ROI")
    lblROIMinSize.grid(row=3, column=0)
    varROIMinSize = tk.IntVar(value=30)
    intROIMinSize = tk.Spinbox(lblfRoiDetection, from_=0, to=100, textvariable=varROIMinSize, width=5, command=intDiff_ReplotROI)
    intROIMinSize.grid(row=3,column=1)
    tk.Label(lblfRoiDetection, text="%").grid(row=3, column=2)    

    lblfRoi = tk.LabelFrame(toolFrame, text="ROI")
    lblfRoi.pack()
    tk.Label(lblfRoi, text="Select ROI").grid(row=0, column=0)
    varROI = tk.IntVar(value=0)
    scaleROI = tk.Scale(lblfRoi, variable=varROI, from_=0, to=0, orient="horizontal", command=ScaleDiff_ReplotROI, showvalue=True)
    scaleROI.grid(row=0, column=1)
    btnExportROI = tk.Button(lblfRoi, text="Export ROIs", command=ExportROIs)
    btnExportROI.grid(row=1, column=0, columnspan=2)

    lblDebug = tk.Label(toolFrame)
    lblDebug.pack()

    figure = plt.Figure(figsize=(6,6), dpi=100)
    figure.tight_layout(pad=200.32)
    ax1 = figure.add_subplot(221)  
    ax2 = figure.add_subplot(222,projection="3d") 
    ax3 = figure.add_subplot(223)  
    ax4 = figure.add_subplot(224) 
    ax1.set_title("Diff Maximum")
    ax2.set_title("Diff 3D Projection")
    ax3.set_title("Detected Neuron areas")
    print()

    #axslider_roi = figure.add_axes([ax4.get_position().x0, ax4.get_position().y1, 0.3, 0.03])
    #s_time = Slider(axslider_roi, 'ROI', 0, 30, valinit=0)

    canvas = FigureCanvasTkAgg(figure, plotFrame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()
    root.mainloop()