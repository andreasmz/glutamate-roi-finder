import sys, os
if __name__ == "__main__":
    glutamate_roi_finder_Path = os.path.join(os.path.join(__file__, os.pardir), os.pardir)
    glutamate_roi_finder_Path = os.path.abspath(glutamate_roi_finder_Path)
    sys.path.insert(1, glutamate_roi_finder_Path)


import glutamate_roi_finder.gui.window as window
import glutamate_roi_finder.gui.settings as settings
import threading

def Start():
    settings.UserSettings.ReadSettings()
    window.GUI.GUI()

def Start_Background():
    task = threading.Thread(target=Start)
    task.start()

def API_GUI():
    return window.GUI

def API_IJ():
    return window.GUI.ij

def API_IMG():
    return window.GUI.IMG

def API_ROI_IMG():
    return window.GUI.ROI_IMG
    
if __name__ == "__main__":
    Start()

