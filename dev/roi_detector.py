import tkinter as tk



root = tk.Tk()
root.title("Glutamte Image ROI Detector")

mainMenu = tk.Menu()
root.config(menu=mainMenu)
menuImageJ = tk.Menu(mainMenu)
mainMenu.add_cascade("ImageJ",menu=menuImageJ)

menuImageJ.add_command(label="Read Image")

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