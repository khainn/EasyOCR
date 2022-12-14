from typing import Union
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import Services 
from io import BytesIO


app = FastAPI()


@app.post("/Info/CCCDVN/")
async def ExportInfo_CCCD_VN( file: Union[UploadFile, None] = None):
    if file.filename == '':
        return {"message": "No upload file sent"}
    else:
        img = await file.read()        
        Info = Services.GetInfo_CCCD_VN(img)
        return Info

@app.post("/Info/DriverLicenseUS/")
async def ExportInfo_DriverLicense_US( file: Union[UploadFile, None] = None):
    if file.filename == '':
        return {"message": "No upload file sent"}
    else:
        img = await file.read()
        Info = Services.GetInfo_DriverLicense_US(img)
        return Info
            
    

@app.get("/")
async def main():
    content = """
<body>
<span> Can Cuoc Cong Dan Viet nam </span>
<form action="/Info/CCCDVN/" enctype="multipart/form-data" method="post">
<input name="file" type="file" multiple>
<input type="submit">
</form>

<span> Driver License US </span>
<form action="/Info/DriverLicenseUS/" enctype="multipart/form-data" method="post">
<input name="file" type="file" multiple>
<input type="submit">
</form>

</body>
    """
    return HTMLResponse(content=content)
