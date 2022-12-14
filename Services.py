import easyocr
import postprocess.GetAllDatas as GetData
import json
import cv2
import numpy as np
from fastapi import encoders
from fastapi import responses

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class NpDecoder(json.JSONDecoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)



def GetInfo_CCCD_VN(Image):
    reader = easyocr.Reader(['vi'])

    dict_json = GetCategoryForm("CCCD VN")

    text_results = reader.readtext(Image, beamWidth= 5, text_threshold = 0.7, low_text = 0.4, 
            link_threshold = 0.6, ycenter_ths = 0.5, height_ths = 0.5,
                width_ths = 0.6, y_ths = 0.5, x_ths = 1.0)

    DataForm = GetData.CCCD_VN_postprocess(text_results, dict_json)
    for t in text_results:
        print(t[0:2])
    Result = json.dumps(DataForm, cls=NpEncoder, ensure_ascii = False)
    content = json.loads(Result)
    
    return responses.JSONResponse(content=content)


def GetInfo_DriverLicense_US(Image):
    reader = easyocr.Reader(['en'])

    dict_json = GetCategoryForm("Driver License")

    text_results = reader.readtext(Image, beamWidth= 5, text_threshold = 0.7, low_text = 0.4, 
        link_threshold = 0.4, ycenter_ths = 0.5, height_ths = 0.5,
            width_ths = 0.5, y_ths = 0.5, x_ths = 1.0) 

    DataForm = GetData.DriverLicense_postprocess(text_results, dict_json)
    Result = json.dumps(DataForm, cls=NpEncoder, ensure_ascii = False)
    content = json.loads(Result)      

    return responses.JSONResponse(content=content)


def GetCategoryForm(CategoryFormName):
    dict_json = {}
    try:
        CategoryFileName = LoadPathJsonForm(CategoryFormName)
        f = open(CategoryFileName)
        dict_json = json.load(f)
        return dict_json
    except:
        print("Error open file Category json")
        return dict_json


def LoadPathJsonForm(CategoryFormName):    #    "CCCD VN"
    dictCategory = LoadJsonConfigFile()
    CategoryFileName = ""
    try:
        CategoryFileName = dictCategory[CategoryFormName]   #   "CCCD VN": "FormJson/CCCD_VN.json"
        print("CategoryFileName: ", CategoryFileName)
        return CategoryFileName
    except:
        print("Error load file Json Form")
        return CategoryFileName

def LoadJsonConfigFile(configFile = "FormJson/configMapForm.json"):
    dictCategory = {}
    try:
        f= open(configFile)
        dictCategory = json.load(f)
        return dictCategory
    except:
        print("Error Open config file")
        return dictCategory


   
