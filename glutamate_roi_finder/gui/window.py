import glutamate_roi_finder.gui.settings as settings
from glutamate_roi_finder.utils.image import Img
from glutamate_roi_finder.utils.detection import ROIImage

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
from matplotlib import cm
import pickle

from scyjava import jimport

class _GUI:

    def __init__(self):
        self.root = None
        self.ij = None
        self.ij_load = True
        self.RM = None
        self.estParams = None
        self.IMG = Img()
        self.ROI_IMG = ROIImage()

    def GUI(self):
        self.root = tk.Tk()
        self.root.title("Glutamte Image ROI Detector")
        if (settings.UserSettings.Settings == None):
            messagebox.showerror("Glutamate Roi Finder", "The settings.json couldn't be read")
            exit()

        self.statusFrame = tk.Frame(self.root)
        self.statusFrame.pack(side=tk.BOTTOM, fill="x", expand=False)
        self.toolFrame = tk.Frame(self.root, width=500)
        self.toolFrame.pack(side=tk.LEFT, fill="y", expand=False)
        self.plotFrame = tk.Frame(self.root)
        self.plotFrame.pack(side=tk.LEFT, fill="both", expand=True)

        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.menuImageJ = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="ImageJ",menu=self.menuImageJ)

        self.menuImageJ.add_command(label="Start ImageJ", command=self._MenuStartImageJ_Click)
        self.menuImageJ.add_command(label="Read Image",state="disabled", command=self.LoadFromImageJ)
        self.menuImageJ.add_command(label="Save dump",state="disabled", command=self._Debug_Save)
        self.menuImageJ.add_command(label="Load dump",state="normal", command=self._Debug_Load)

        self.varProgMain = tk.DoubleVar()
        self.progMain = ttk.Progressbar(self.statusFrame,orient="horizontal", length=200, variable=self.varProgMain)
        self.progMain.pack(side=tk.LEFT)
        self.lblProgMain = tk.Label(self.statusFrame, text="", relief=tk.SUNKEN,borderwidth=1)
        self.lblProgMain.pack(side=tk.LEFT, padx=(10,10))
        self.lblImgInfo = tk.Label(self.statusFrame, text="No image selected",borderwidth=1, relief=tk.SUNKEN)
        self.lblImgInfo.pack(side=tk.LEFT, padx=(10, 10))
        self.lblStatusInfo = tk.Label(self.statusFrame, text="", borderwidth=1, relief=tk.SUNKEN)
        self.lblStatusInfo.pack(side=tk.LEFT, padx=(10, 10))

        self.lblfParameterEst = tk.LabelFrame(self.toolFrame, text="Paremeter estimation")
        self.lblfParameterEst.pack(fill="x")
        self.lblParameterEst = tk.Label(self.lblfParameterEst, text="", anchor="e")
        self.lblParameterEst.pack(side=tk.LEFT)
        self.btnUseEstimation = tk.Button(self.lblfParameterEst, text="Use", state="disabled", command=self._BtnUseEst_Click)
        self.btnUseEstimation.pack(side=tk.RIGHT)

        self.lblfDiffDetection = tk.LabelFrame(self.toolFrame, text="Diff detection")
        self.lblfDiffDetection.pack(fill="x")
        self.lblScaleDiffInfo = tk.Label(self.lblfDiffDetection, text="threshold")
        self.lblScaleDiffInfo.grid(row=0, column=0, columnspan=2)
        self.varDiff = tk.IntVar(value=20)
        self.intDiff = tk.Spinbox(self.lblfDiffDetection, from_=1, to=200, textvariable=self.varDiff,width=5, command=self._ReplotTab1)
        self.intDiff.grid(row=1, column=0)
        self.scaleDiff = tk.Scale(self.lblfDiffDetection, variable=self.varDiff, from_=1, to=200, orient="horizontal", command=self._ScaleDiff_Replot, showvalue=False)
        self.scaleDiff.grid(row=1, column=1)

        self.lblfRoiDetection = tk.LabelFrame(self.toolFrame, text="ROI Detection")
        self.lblfRoiDetection.pack(fill="x")
        tk.Label(self.lblfRoiDetection, text="ROI radius").grid(row=0, column=0)
        self.varROIRadius = tk.IntVar(value=6)
        self.intROIRadius = tk.Spinbox(self.lblfRoiDetection, from_=1, to=50, textvariable=self.varROIRadius, width=5, command=self._ReplotTab1_ROI)
        self.intROIRadius.grid(row=0, column=1)
        tk.Label(self.lblfRoiDetection, text="px").grid(row=0, column=2)
        self.lblROIMinSize = tk.Label(self.lblfRoiDetection, text="Minimum coverage")
        self.lblROIMinSize.grid(row=3, column=0)
        self.varROIMinSize = tk.IntVar(value=60)
        self.intROIMinSize = tk.Spinbox(self.lblfRoiDetection, from_=0, to=100, textvariable=self.varROIMinSize, width=5, command=self._ReplotTab1_ROI)
        self.intROIMinSize.grid(row=3,column=1)
        tk.Label(self.lblfRoiDetection, text="%").grid(row=3, column=2)    

        self.lblfRoi = tk.LabelFrame(self.toolFrame, text="ROI")
        self.lblfRoi.pack(fill="x")
        tk.Label(self.lblfRoi, text="Select ROI").grid(row=0, column=0)
        self.varROI = tk.IntVar(value=0)
        self.scaleROI = tk.Scale(self.lblfRoi, variable=self.varROI, from_=0, to=0, orient="horizontal", command=self._ScaleDiff_ReplotROISelected, showvalue=True)
        self.scaleROI.grid(row=0, column=1)
        self.btnExportROI = tk.Button(self.lblfRoi, text="Export ROIs", command=self.ExportROIs)
        self.btnExportROI.grid(row=1, column=0, columnspan=2)

        self.figure1 = plt.Figure(figsize=(6,6), dpi=100)
        self.figure1.tight_layout(pad=200.32)
        self.ax1 = self.figure1.add_subplot(221)  
        self.ax2 = self.figure1.add_subplot(222,projection="3d") 
        self.ax3 = self.figure1.add_subplot(223)  
        self.ax4 = self.figure1.add_subplot(224) 
        self.ax1.set_title("Diff Maximum")
        self.ax2.set_title("Diff 3D Projection")
        self.ax3.set_title("Detected Neuron areas")
        print()

        #axslider_roi = figure.add_axes([ax4.get_position().x0, ax4.get_position().y1, 0.3, 0.03])
        #s_time = Slider(axslider_roi, 'ROI', 0, 30, valinit=0)

        self.canvas = FigureCanvasTkAgg(self.figure1, self.plotFrame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()
        self.root.mainloop()


    def LoadFromImageJ(self):
        if self.ij is None:
            messagebox.showerror("Glutamate Roi Finder", "Please first start ImageJ")
            return
        self.IMG.img = self.ij.py.active_xarray() 
        if self.IMG.img is None:
            self.lblStatusInfo["text"] = "Please first select an image in ImageJ"
            return
        self.lblStatusInfo["text"] = ""
        
        self.IMG.img = np.array(self.IMG.img)
        self.IMG.img = self.IMG.img.astype("int16")
        self.IMG.ImgProvided()
        _size = round(sys.getsizeof(self.IMG.img)/(1024**2),2)
        self.lblImgInfo["text"] = f"Image: {self.IMG.img.shape}, dtype={self.IMG.img.dtype}, size = {_size} MB"
        self.ParameterEst()
        self._ReplotTab1()

    def ParameterEst(self):
        if self.IMG.imgDiffMaxTime is None:
            return
        self.estParams = self.ROI_IMG.EstimateParameters(self.IMG.imgDiffMaxTime)
        self.btnUseEstimation["state"] = "normal"
        self.lblParameterEst["text"] = f"Suggestion for parameters\nThreshold: {self.estParams['Threshold']}\nROI Size: 6\nMin Coverage: 60"

    def ExportROIs(self):
        if self.ij is None:
            messagebox.showerror("Glutamate Roi Finder", "Please first start ImageJ")
            return
        if self.ROI_IMG.rois is None:
            return
        #if (self.RM is None):
        #    messagebox.showwarning("Glutamate Roi Finder", "Attention: Is the ROI Manager in ImageJ opened? If not, open it now or ImageJ will prompt out an error message refusing to open the ROIManager until restart")
        self.ij.py.run_macro("roiManager('show all');")
        self.RM = self.ij.RoiManager.getRoiManager()
        radius = self.varROIRadius.get()
        for i in  range(len(self.ROI_IMG.rois)):
            roiPoint = self.ROI_IMG.rois[i]
            roi = self.OvalRoi(roiPoint[0]-radius,roiPoint[1]-radius, 2*radius, 2*radius)
            roi.setName(f"ROI {i+1} ({roiPoint[0]}, {roiPoint[1]})")
            self.RM.addRoi(roi)

    def StartImageJ(self):
        self.ij_load = True
        self.ij = imagej.init(settings.UserSettings.imageJPath, mode='interactive')
        #self.RM = jimport("ij.plugin.frame.RoiManager")
        self.OvalRoi = jimport('ij.gui.OvalRoi')
        self.ij.ui().showUI()
        self._ImageJReady()

        self.ij_load = False

    def _ImageJReady(self):
        self.menuImageJ.entryconfig("Read Image", state="normal")
        self.menuImageJ.entryconfig("Save dump", state="normal")

    def _ReplotTab1(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.ax1.set_title("Diff Maximum")
        self.ax2.set_title("Diff 3D Projection")
        if self.IMG.imgDiffMaxTime is None:
            return
        
        self.ax1.imshow(self.IMG.imgDiffMaxTime)

        X = np.arange(0,self.IMG.imgDiffMaxTime.shape[0])
        Y = np.arange(0,self.IMG.imgDiffMaxTime.shape[1])
        X, Y = np.meshgrid(X, Y)
        #C = (detectDiff.imgDiffMax > scaleDiff.get()).astype(int)
        #lblDebug = str(C)
        self.ax2.plot_surface(X,Y, self.IMG.imgDiffMaxTime, cmap=cm.coolwarm)
        self._ReplotTab1_ROI()

    def _ReplotTab1_ROI(self):
        self.ax3.clear()
        self.ax4.clear()
        self.ax3.set_title("Detected Neuron areas")

        if self.IMG.imgDiffMaxTime is None:
            self.canvas.draw()
            return
        
        radius = self.varROIRadius.get()
        
        self.ROI_IMG.SetImg(self.IMG.imgDiffMaxTime, self.scaleDiff.get())
        self.ROI_IMG.LabelImg(radius, self.varROIMinSize.get()/100)

        self._ax3patches = {}
        for roi in self.ROI_IMG.rois:
            color = "red"
            c = Circle(roi, radius, color=color, fill=False)
            self.ax3.add_patch(c)
            self._ax3patches[roi] = c
        self.scaleROI.set(0)
        self.scaleROI.configure(to=len(self.ROI_IMG.rois))

        self.ax3.imshow(self.ROI_IMG.imgThresholded)
        self.canvas.draw()

    def _ReplotTab1_ROISelected(self):
        self.ax4.clear()

        selectedROI = None
        selectedIndex = self.varROI.get()
        radius = self.varROIRadius.get()

        if (selectedIndex == 0):
            return
        
        if (selectedIndex > len(self.ROI_IMG.rois)):
            return
        
        if self.IMG.img is None:
            return

        selectedROI = self.ROI_IMG.rois[selectedIndex-1]
        _imgmask, _n = self.IMG.GetImgConv_At(selectedROI,radius)
        _signal = np.sum(_imgmask, axis=(1,2))/_n
        self.ax4.plot(_signal)
        self.ax4.set_ylabel("Brightness")
        self.ax4.set_xlabel("Frame")
        self.ax4.set_title("ROI" + str(selectedIndex))

        for roi, c in self._ax3patches.items():
            if roi == selectedROI:
                c.set_color("yellow")
            else:
                c.set_color("red")

        self.canvas.draw()

    def _Debug_Save(self):
        savePath = os.path.join(settings.UserSettings.UserPath, "img.dump")
        print("Saved dump to", savePath)
        with open(savePath, 'wb') as outp:
            pickle.dump(self.IMG.img, outp, pickle.HIGHEST_PROTOCOL)

    def _Debug_Load(self):
        savePath = os.path.join(settings.UserSettings.UserPath, "img.dump")
        with open(savePath, 'rb') as intp:
            self.IMG.img = pickle.load(intp)
            self.IMG.ImgProvided()
        self._ImageJReady()
        _size = round(sys.getsizeof(self.IMG.img)/(1024**2),2)
        self.lblImgInfo["text"] = f"Image: {self.IMG.img.shape}, dtype={self.IMG.img.dtype}, size = {_size} MB"
        self.ParameterEst()
        self._ReplotTab1()

    def _MenuStartImageJ_Click(self):
        if (not os.path.exists(settings.UserSettings.imageJPath)):
            messagebox.showerror("Glutamate Roi Finder", "The given ImageJ path doesn't exist")
            return

        self.lblProgMain["text"] = "Starting ImageJ..."
        self.menuImageJ.entryconfig("Start ImageJ", state="disabled")

        def _ProgStartingImgJ_Step():
            self.progMain.step(10)
            if self.ij_load is True:
                self.root.after(50, _ProgStartingImgJ_Step)
            else:
                self.progMain.configure(mode="determinate")
                self.varProgMain.set(0)
                self.lblProgMain["text"] = ""

        self.progMain.configure(mode="indeterminate")
        _ProgStartingImgJ_Step()
        
        self.ijthread = threading.Thread(target=self.StartImageJ)
        self.ijthread.start()

    def _ScaleDiff_Replot(self, val):
        self._ReplotTab1()

    def _ScaleDiff_ReplotROI(self, val):
        self._ReplotTab1_ROI()

    def _ScaleDiff_ReplotROISelected(self, val):
        self._ReplotTab1_ROISelected()
    
    def _BtnUseEst_Click(self):
        if (self.estParams is None):
            return
        self.varDiff.set(self.estParams["Threshold"])
        self.varROIRadius.set(6)
        self.varROIMinSize.set(60)
        self._ReplotTab1_ROI()

GUI = _GUI()