import json
import glob
import shutil
import os

from io import BytesIO
import numpy as np
import io
import cv2
import PIL
from PIL import Image
import easyocr
from postprocess.line import line_postprocess


reader = easyocr.Reader(['vi'])


class VRegister():
    def __init__(self):
        pass
    def preprocess(self, data):
        image_path = data[0].get("data")
        if image_path is None:
            image_path = data[0].get("body")
        image = Image.open(io.BytesIO(image_path))
        image_data = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return image_data

    def inference(self, img):
        results= reader.readtext(img,canvas_size=1024)
        json=line_postprocess(results,img)
        return [json]

    def postprocess(self, inference_output):
        return inference_output

    def handle(self, data, context):
        model_input = self.preprocess(data)
        model_out = self.inference(model_input)
        return self.postprocess(model_out)

_service = VRegister()

# def handle(data, context):
#     if data is None:
#         return None

#     return _service.handle(data, context)


img=cv2.imread('images/hai-xe-mo-to-khung-nghi-bi-lam-gia-giay-to1.jpg')
kkk=_service.inference(img)

print(kkk)


