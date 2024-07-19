import os
import json


ImageJPath = None
parentPath = None

def ReadSettings():
    global ImageJPath, parentPath
    parentPath = os.path.abspath(os.path.join(__file__, os.pardir))
    parentPath = os.path.abspath(os.path.join(parentPath, os.pardir))
    settingsPath = os.path.join(parentPath, "settings.json")
    if not os.path.isfile(settingsPath):
        print("settings.json not found")
        return
    try:
        with open(settingsPath) as f:
            d = json.load(f)
            if "ImageJPath" not in d:
                print("ImageJPath property in settings.json not found")
                return
            ImageJPath = d["ImageJPath"]
            print(d["ImageJPath"])
    except Exception:
        print("Can't open settings.json")
        return