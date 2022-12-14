***run**
```
python main.py
```

```
model-archiver --model-name ocr --model-path ./ --handler api:handle --export-path ./

mxnet-model-server --start --mms-config config.properties --model-store ./
curl -X POST "localhost:5556/models?url=ocr.mar&batch_size=1&max_batch_delay=10&initial_workers=1"
```



B1: Bổ sung file Json cấu trúc thông tin của thẻ mới trong file configMapForm.json

{
   "CCCD VN": "FormJson/CCCD_VN.json",
   "Driver License": "FormJson/DriverLicense.json"
}

B2: Xây dụng cấu trúc thông tin file Json cho category thẻ mới:

{
   "Category": "new name of category card",
   "Number": {
       "bbox": [],
       "value": ""
   },
   "Full name": {
       "bbox": [],
       "value": ""
   },
   "Date Of Birth": {
       "bbox": [],
       "value": ""
   },
   "Sex": {
       "bbox": [],
       "value": ""
   },
   "Nationality": {
       "bbox": [],
       "value": ""
   },
   "Place of origin": {
       "bbox": [],
       "value": ""
   },
   "Date of expiry": {
       "bbox": [],
       "value": ""
   }
 
}

B3: Viết Hàm lưu dữ liệu từ quá trình text detection vào Json tương ứng với từng trường thông tin.
B4: Update hàm PostProcess trong main.py
