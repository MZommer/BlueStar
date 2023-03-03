from PIL import ImageColor
import json
import numpy as np


### JSON Reader functions ###

def loadJson(JsonString):
    try:
        return json.loads(JsonString)
    except:
        return json.loads("(".join(JsonString.split("(")[1:])[:-1])


def openJson(path):
    try:
        return json.load(open(path, encoding="utf_8"))
    except:
        return loadJson(open(path, encoding="utf_8").read())


### Resolvers ###

def CoachCountResolver(CoachCount):
    if isinstance(CoachCount, str):
        return {
            "Solo": 1,
            "Duet": 2,
            "Duo": 2,
            "Trio": 3,
            "Quartet": 4,
            "Quatuor": 4
        }[CoachCount]
    return CoachCount


### Array functions ###

def getClosestIndex(arr, value):
    return np.abs(np.subtract.outer(arr, value)).argmin(0)


def getClosestValue(arr, value):
    return arr[getClosestIndex(arr, value)]


### Color functions ###

def hex2perc(hexString):
    percArr = [1]
    if hexString.lower().startswith("0xff"):
        hexString = "#" + hexString[4:]
    elif not hexString.startswith("#") and len(hexString) == 6:
        hexString = "#" + hexString
    for color in ImageColor.getcolor(hexString, "RGB"):
        value = round((color / 255), 6)
        value = int(value) if value % 1 == 0 else value
        percArr.append(value)
    return percArr
