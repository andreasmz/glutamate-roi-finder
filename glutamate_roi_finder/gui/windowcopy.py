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

class _GUI():
    root = None

    def GUI(self):
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

        menuImageJ.add_command(label="Start ImageJ")
        menuImageJ.add_command(label="Read Image",state="disabled")
        menuImageJ.add_command(label="Save dump",state="disabled")
        menuImageJ.add_command(label="Load dump",state="normal")

        root.mainloop()
        return

        progStartingImgJ = ttk.Progressbar(toolFrame,orient="horizontal", mode="indeterminate", length=200)
        lblStartImageJ = tk.Label(toolFrame,text="Starting ImageJ...")
        lblImgInfo = tk.Label(toolFrame)

        lblfDiffDetection = tk.LabelFrame(toolFrame, text="Diff detection")
        lblfDiffDetection.pack()
        lblScaleDiffInfo = tk.Label(lblfDiffDetection, text="threshold")
        lblScaleDiffInfo.grid(row=0, column=0, columnspan=2)
        varDiff = tk.IntVar(value=20)
        intDiff = tk.Spinbox(lblfDiffDetection, from_=1, to=200, textvariable=varDiff,width=5)
        intDiff.grid(row=1, column=0)
        scaleDiff = tk.Scale(lblfDiffDetection, variable=varDiff, from_=1, to=200, orient="horizontal", showvalue=False)
        scaleDiff.grid(row=1, column=1)

        lblfRoiDetection = tk.LabelFrame(toolFrame, text="ROI Detection")
        lblfRoiDetection.pack()
        tk.Label(lblfRoiDetection, text="ROI radius").grid(row=0, column=0)
        varROIRadius = tk.IntVar(value=10)
        intROIRadius = tk.Spinbox(lblfRoiDetection, from_=1, to=25, textvariable=varROIRadius, width=5)
        intROIRadius.grid(row=0, column=1)
        tk.Label(lblfRoiDetection, text="px").grid(row=0, column=2)
        lblROIMinSize = tk.Label(lblfRoiDetection, text="Minimum size of ROI")
        lblROIMinSize.grid(row=3, column=0)
        varROIMinSize = tk.IntVar(value=30)
        intROIMinSize = tk.Spinbox(lblfRoiDetection, from_=0, to=100, textvariable=varROIMinSize, width=5)
        intROIMinSize.grid(row=3,column=1)
        tk.Label(lblfRoiDetection, text="%").grid(row=3, column=2)    

        lblfRoi = tk.LabelFrame(toolFrame, text="ROI")
        lblfRoi.pack()
        tk.Label(lblfRoi, text="Select ROI").grid(row=0, column=0)
        varROI = tk.IntVar(value=0)
        scaleROI = tk.Scale(lblfRoi, variable=varROI, from_=0, to=0, orient="horizontal", showvalue=True)
        scaleROI.grid(row=0, column=1)
        btnExportROI = tk.Button(lblfRoi, text="Export ROIs")
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


GUI = _GUI()