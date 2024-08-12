import glutamate_roi_finder.gui.settings as settings
import glutamate_roi_finder.utils.diffDetection as detectDiff
import glutamate_roi_finder.utils.roiDetection as roiDetect

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

class _GUI:
    def ImageJReady(self):
        self.menuImageJ.entryconfig("Read Image", state="normal")
        self.menuImageJ.entryconfig("Save dump", state="normal")

    def StartImageJ(self):
        self.ij = imagej.init(settings.ImageJPath, mode='interactive')
        self.RM = jimport("ij.plugin.frame.RoiManager")
        self.OvalRoi = jimport('ij.gui.OvalRoi')
        self.ij.ui().showUI()
        self.ImageJReady()
        self.progStartingImgJ.pack_forget()
        self.lblStartImageJ.pack_forget()

        self.lblImgInfo["text"] = "No image selected"
        self.lblImgInfo.pack()
        self.ij_load = None

    def MbtnStartImageJ_Click(self):
        if (settings.ImageJPath is None):
            return
        if (not os.path.exists(settings.ImageJPath)):
            messagebox.showerror("Glutamate Roi Finder", "The given ImageJ path doesn't exist")
            return

        self.lblStartImageJ.pack()
        self.ij_load = True

        self.menuImageJ.entryconfig("Start ImageJ", state="disabled")

        def ProgStartingImgJ_Step():
            self.progStartingImgJ.step(10)
            if self.ij_load is not None:
                self.root.after(50, ProgStartingImgJ_Step)
        self.progStartingImgJ.pack()
        ProgStartingImgJ_Step()
        
        t = threading.Thread(target=self.StartImageJ)
        t.start()
    
    def MBtnReadImage(self):
        detectDiff.img = self.ij.py.active_xarray() 
        if detectDiff.img is None:
            return
        detectDiff.img = np.array(detectDiff.img)
        if (np.max(detectDiff.img) <= 2**15):
            detectDiff.img = detectDiff.img.astype("int16")
        if detectDiff.img is not None:
            detectDiff.imgConv = detectDiff.ConvTask()
            self.lblImgInfo["text"] = f"{detectDiff.img.shape}, dtype={detectDiff.img.dtype}"
            detectDiff.ProcessImg()
            self.Replot()
            print("Img Size =", round(sys.getsizeof(detectDiff.imgDiffMax)/(1024**2),2),"MB")
        else:
            self.lblImgInfo["text"] = "No image selected"

    def Replot(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.ax1.set_title("Diff Maximum")
        self.ax2.set_title("Diff 3D Projection")
        if detectDiff.imgDiffMax is None:
            return
        
        self.ax1.imshow(detectDiff.imgDiffMax)

        X = np.arange(0,detectDiff.imgDiffMax.shape[0])
        Y = np.arange(0,detectDiff.imgDiffMax.shape[1])
        X, Y = np.meshgrid(X, Y)
        #C = (detectDiff.imgDiffMax > scaleDiff.get()).astype(int)
        #lblDebug = str(C)
        self.ax2.plot_surface(X,Y, detectDiff.imgDiffMax)
        self.ReplotROI()

    def ReplotROI(self):
        self.ax3.clear()
        self.ax4.clear()
        self.ax3.set_title("Detected Neuron areas")

        if detectDiff.imgDiffMax is None:
            return

        detectDiff.Diff_Mask(self.scaleDiff.get())
        roiDetect.Label(detectDiff.imgDiffRegions, radius=self.varROIRadius.get(), minROISize=self.varROIMinSize.get()/100)

        selectedROI = None
        
        if (self.varROI.get() != 0 and self.varROI.get() <= len(roiDetect.rois)):
            roiCentroid = roiDetect.rois[self.varROI.get()-1]
            selectedROI = roiCentroid
            if (detectDiff.imgConv is not None):
                self.ax4.plot(detectDiff.imgConv[:, roiCentroid[0], roiCentroid[1]])
                self.ax4.set_title("ROI" + str(self.varROI.get()))

        self.ax3.imshow(detectDiff.imgDiffRegions)
        for roi in roiDetect.rois:
            color = "red" 
            if (selectedROI == roi):
                color = "yellow"
            c = Circle(roi, self.varROIRadius.get(), color=color, fill=False)
            self.ax3.add_patch(c)
        self.scaleROI.configure(to=len(roiDetect.rois))

        self.canvas.draw()

    def ExportROIs(self):
        if self.ij is None:
            print("ij not started")
            return
        rm = self.RM.getRoiManager()
        for roi in roiDetect.rois:
            roi = self.OvalRoi(roi[0],roi[1], self.varROIRadius.get(), self.varROIRadius.get())
            rm.addRoi(roi)

    def ScaleDiff_Replot(self, val):
        self.Replot()

    def ScaleDiff_ReplotROI(self, val):
        self.ReplotROI()

    def intDiff_Replot(self):
        self.Replot()
    
    def intDiff_ReplotROI(self):
        self.ReplotROI()

    def _Debug_Save(self):
        savePath = os.path.join(settings.settingsPath, "img.dump")
        print("Saved dump to", savePath)
        with open(savePath, 'wb') as outp:
            pickle.dump(detectDiff.img, outp, pickle.HIGHEST_PROTOCOL)

    def _Debug_Load(self):
        savePath = os.path.join(settings.settingsPath, "img.dump")
        with open(savePath, 'rb') as intp:
            detectDiff.img = pickle.load(intp)
        detectDiff.ProcessImg()
        self.ImageJReady()
        self.lblImgInfo["text"] = "Img from dump"
        self.Replot()

    def GUI(self):
        self.root = tk.Tk()
        self.root.title("Glutamte Image ROI Detector")
        if (settings.ImageJPath is None):
            messagebox.showerror("Glutamate Roi Finder", "The settings.json couldn't be read")
            exit()

        self.toolFrame = tk.Frame(self.root)
        self.toolFrame.pack(side=tk.LEFT, fill="both", expand=False)

        self.plotFrame = tk.Frame(self.root)
        self.plotFrame.pack(side=tk.RIGHT, fill="both", expand=True)

        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.menuImageJ = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="ImageJ",menu=self.menuImageJ)

        self.menuImageJ.add_command(label="Start ImageJ", command=self.MbtnStartImageJ_Click)
        self.menuImageJ.add_command(label="Read Image",state="disabled", command=self.MBtnReadImage)
        self.menuImageJ.add_command(label="Save dump",state="disabled", command=self._Debug_Save)
        self.menuImageJ.add_command(label="Load dump",state="normal", command=self._Debug_Load)

        self.progStartingImgJ = ttk.Progressbar(self.toolFrame,orient="horizontal", mode="indeterminate", length=200)
        self.lblStartImageJ = tk.Label(self.toolFrame,text="Starting ImageJ...")
        self.lblImgInfo = tk.Label(self.toolFrame)

        self.lblfDiffDetection = tk.LabelFrame(self.toolFrame, text="Diff detection")
        self.lblfDiffDetection.pack()
        self.lblScaleDiffInfo = tk.Label(self.lblfDiffDetection, text="threshold")
        self.lblScaleDiffInfo.grid(row=0, column=0, columnspan=2)
        self.varDiff = tk.IntVar(value=20)
        self.intDiff = tk.Spinbox(self.lblfDiffDetection, from_=1, to=200, textvariable=self.varDiff,width=5, command=self.intDiff_Replot)
        self.intDiff.grid(row=1, column=0)
        self.scaleDiff = tk.Scale(self.lblfDiffDetection, variable=self.varDiff, from_=1, to=200, orient="horizontal", command=self.ScaleDiff_Replot, showvalue=False)
        self.scaleDiff.grid(row=1, column=1)

        self.lblfRoiDetection = tk.LabelFrame(self.toolFrame, text="ROI Detection")
        self.lblfRoiDetection.pack()
        tk.Label(self.lblfRoiDetection, text="ROI radius").grid(row=0, column=0)
        self.varROIRadius = tk.IntVar(value=10)
        self.intROIRadius = tk.Spinbox(self.lblfRoiDetection, from_=1, to=25, textvariable=self.varROIRadius, width=5, command=self.intDiff_ReplotROI)
        self.intROIRadius.grid(row=0, column=1)
        tk.Label(self.lblfRoiDetection, text="px").grid(row=0, column=2)
        self.lblROIMinSize = tk.Label(self.lblfRoiDetection, text="Minimum size of ROI")
        self.lblROIMinSize.grid(row=3, column=0)
        self.varROIMinSize = tk.IntVar(value=30)
        self.intROIMinSize = tk.Spinbox(self.lblfRoiDetection, from_=0, to=100, textvariable=self.varROIMinSize, width=5, command=self.intDiff_ReplotROI)
        self.intROIMinSize.grid(row=3,column=1)
        tk.Label(self.lblfRoiDetection, text="%").grid(row=3, column=2)    

        self.lblfRoi = tk.LabelFrame(self.toolFrame, text="ROI")
        self.lblfRoi.pack()
        tk.Label(self.lblfRoi, text="Select ROI").grid(row=0, column=0)
        self.varROI = tk.IntVar(value=0)
        self.scaleROI = tk.Scale(self.lblfRoi, variable=self.varROI, from_=0, to=0, orient="horizontal", command=self.ScaleDiff_ReplotROI, showvalue=True)
        self.scaleROI.grid(row=0, column=1)
        self.btnExportROI = tk.Button(self.lblfRoi, text="Export ROIs", command=self.ExportROIs)
        self.btnExportROI.grid(row=1, column=0, columnspan=2)

        self.lblDebug = tk.Label(self.toolFrame)
        self.lblDebug.pack()

        self.figure = plt.Figure(figsize=(6,6), dpi=100)
        self.figure.tight_layout(pad=200.32)
        self.ax1 = self.figure.add_subplot(221)  
        self.ax2 = self.figure.add_subplot(222,projection="3d") 
        self.ax3 = self.figure.add_subplot(223)  
        self.ax4 = self.figure.add_subplot(224) 
        self.ax1.set_title("Diff Maximum")
        self.ax2.set_title("Diff 3D Projection")
        self.ax3.set_title("Detected Neuron areas")
        print()

        #axslider_roi = figure.add_axes([ax4.get_position().x0, ax4.get_position().y1, 0.3, 0.03])
        #s_time = Slider(axslider_roi, 'ROI', 0, 30, valinit=0)

        self.canvas = FigureCanvasTkAgg(self.figure, self.plotFrame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()
        self.root.mainloop()

GUI = _GUI()