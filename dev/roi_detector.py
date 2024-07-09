import tkinter as tk
from tkinter import ttk
import imagej
import threading
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def StartImageJ():
    global ij
    path1 = "C:\\Users\\abril\\Desktop\\Arbeitsprogramme\\fiji-win64\\Fiji.app"
    path2 = "C:\\Users\\abril\\Andreas Eigene Dateien\\Programme\\Fiji.app"

    ij = imagej.init(path1, mode='interactive')
    ij.ui().showUI()
    menuImageJ.entryconfig("Read Image", state="normal")
    progStartingImgJ.pack_forget()
    lblStartImageJ.pack_forget()

    lblImgInfo["text"] = "No image selected"
    lblImgInfo.pack()

def MbtnStartImageJ_Click():
    lblStartImageJ.pack(side=tk.LEFT)

    menuImageJ.entryconfig("Start ImageJ", state="disabled")

    def ProgStartingImgJ_Step():
        progStartingImgJ.step(10)
        root.after(50, ProgStartingImgJ_Step)
    progStartingImgJ.pack(side=tk.LEFT)
    ProgStartingImgJ_Step()
    
    t = threading.Thread(target=StartImageJ)
    t.start()
   
def MBtnReadImage():
    global img
    img = ij.py.active_xarray() 
    if img is None:
        return
    img = np.array(img)
    if (np.max(img) <= 2**15):
        img = img.astype("int16")
    if img is not None:
        lblImgInfo["text"] = f"{img.shape}, dtype={img.dtype}"
        ImageProcessing()
    else:
        lblImgInfo["text"] = "No image selected"

def ImageProcessing():
    global imgDiff, imgDiffMax
    imgDiff = np.diff(img, axis=0)
    imgDiffMax = np.max(imgDiff,axis=0)

def Test():
    ax1.clear()
    ax1.imshow(imgDiffMax)
    canvas.draw()

root = tk.Tk()
root.title("Glutamte Image ROI Detector")

menubar = tk.Menu(root)
root.config(menu=menubar)
menuImageJ = tk.Menu(menubar,tearoff=0)
menubar.add_cascade(label="ImageJ",menu=menuImageJ)

menuImageJ.add_command(label="Start ImageJ", command=MbtnStartImageJ_Click)
menuImageJ.add_command(label="Read Image",state="disabled", command=MBtnReadImage)
menuImageJ.add_command(label="Test",state="normal", command=Test)

progStartingImgJ = ttk.Progressbar(root,orient="horizontal", mode="indeterminate", length=200)
lblStartImageJ = tk.Label(root,text="Starting ImageJ...")
lblImgInfo = tk.Label(root)


figure = plt.Figure(figsize=(6,6), dpi=100)
ax1 = figure.add_subplot()  
canvas = FigureCanvasTkAgg(figure, root)
canvas.get_tk_widget().pack()


root.mainloop()




"""tk1Frame = tk.Frame(master=root)
tk1Frame.pack()




btn1 = tk.Button(master=tk1Frame, text="Save", command=TK_Export)
btn1.pack()
lbl1 = tk.Label(master=tk1Frame, text="bins")
lbl1.pack(side=tk.LEFT)
slid1 = tk.Scale(master=tk1Frame, variable=sld1Val, command=TK_Sld1, from_=1, to=100, orient=tk.HORIZONTAL, showvalue=True)
slid1.set(20)
slid1.pack(side=tk.LEFT)
figure = plt.Figure(figsize=(6,6), dpi=100)
ax1 = figure.add_subplot()  
canvas = FigureCanvasTkAgg(figure, root)
canvas.get_tk_widget().pack()


"""