import requests

def predict(img_path):
    url = "http://192.168.1.24:5555/predictions/ocr"
    files = {'data': open(img_path, 'rb')}
    r = requests.post(url, files=files)
    print(r)
    if r.ok:
       result = r.json()
       print(result)
       return result
    return None
    
predict('/media/tuyai/02B6EA9ED449E460/dat-tuyai/OCR/images/4e2ccfaaf037de5727861847ac5c74dc.jpg')
