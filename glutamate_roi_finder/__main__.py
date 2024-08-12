import sys,os
glutamate_roi_finder_Path = os.path.abspath("")
print(glutamate_roi_finder_Path)
sys.path.insert(1, glutamate_roi_finder_Path)

import glutamate_roi_finder.gui.window as window
import glutamate_roi_finder.gui.settings as settings

if __name__ == "__main__":
    settings.ReadSettings()
    #window.GUI.GUI()