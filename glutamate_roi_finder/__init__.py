import glutamate_roi_finder.gui.window as window
import glutamate_roi_finder.gui.settings as settings

def Start():
    #window.GUI = window._GUI()
    settings.ReadSettings()
    window.GUI.GUI()

class API:
    def GetDiffImg():
        return window.detectDiff.imgDiff