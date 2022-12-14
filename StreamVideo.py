# USB camera display using PyQt and OpenCV, from iosoft.blog
# Copyright (c) Jeremy P Bentham 2019
# Please credit iosoft.blog if you use the information or software in it

VERSION = "Export Infomation Card v0.10"

import sys, time, threading, cv2, json
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor
import queue as Queue
import easyocr
import numpy as np
import postprocess.GetAllDatas as GetData



# Image widget
class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# Main window
class AppWindow(QMainWindow):
    text_update = pyqtSignal(str)

    # Create main window
    def __init__(self, parent=None):     
        self.IMG_SIZE    = 1280,720          # 640,480 or 1280,720 or 1920,1080
        self.IMG_FORMAT  = QImage.Format_RGB888
        self.DISP_SCALE  = 2                # Scaling factor for display image
        self.DISP_MSEC   = 50                # Delay between display cycles
        self.CAP_API     = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
        self.EXPOSURE    = 0                 # Zero for automatic exposure
        self.TEXT_FONT   = QFont("Courier", 10)

        self.camera_num  = 0                 # Default camera (first in list)
        self.image_queue = Queue.Queue()     # Queue to hold images
        self.capturing   = True   
        
        # Flag to indicate capturing  
        self.originalPalette = QApplication.palette()
        self.ImageFileName = ""
        self.CategoryFileName = ""
        self.dict_json = ""
        self.SelectPath = ""
        self.ImgFile = ["jpg", "JPG", "png", "JPEG", "jpeg"]

        self.AvailableCameras = QCameraInfo.availableCameras()
        

        QMainWindow.__init__(self, parent)        
        self.LoadJsonConfigFile()
        self.timer = QTimer(self)
        self.central = QWidget(self)
        self.central.setMinimumSize(900, 600)
    
        self.createInfoGroupTab()
        self.createInfoGroupBox()
        self.createToolBar()

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.InfoGroupTab)
        mainLayout.addWidget(self.InfoGroupBox)
        mainLayout.addStretch(1)

        self.central.setLayout(mainLayout)
        self.setWindowTitle("Export Infomation Card")

        self.setCentralWidget(self.central)
        self.changeStyle('Fusion')


    def createInfoGroupTab(self):
        qfont = QFont('Arial', 12)

        #Create Video Tab
        VideoTab = QGroupBox(self)

        VideoLayout = QVBoxLayout()

        CaptureButton = QPushButton("Captute")
        font = QFont('Arial', 13)
        font.setBold(True)
        CaptureButton.setFont(font)
        CaptureButton.clicked.connect(self.CaptureButtonEvent)

        VideoTab.setLayout(VideoLayout)
        
        self.DisplayVideo = ImageWidget(self)    
        VideoLayout.addWidget(self.DisplayVideo)
        VideoLayout.addSpacing(50)
        VideoLayout.addWidget(CaptureButton)
   
        # Create Image Selection Tab
        ImageTab = QGroupBox()

        SelectImageButton = QPushButton("Select Image")       
        # SelectImageButton.setGeometry(0, 20, 50, 20) 
        SelectImageButton.setFixedSize(120, 30)
        SelectImageButton.setFont(qfont)
        SelectImageButton.clicked.connect(self.SelectFileName)

        self.EditImagePath = QLineEdit(self.SelectPath)
        self.EditImagePath.setReadOnly(True)

        NameLabelImagePath = QLabel('Image path: ', self)
        NameLabelImagePath.setFont(qfont)

        RunButton = QPushButton("RUN")
        RunButton.setFixedSize(130, 50)
        font = QFont('Arial', 13)
        font.setBold(True)
        RunButton.setFont(font)
        RunButton.move(100, 120)
        RunButton.clicked.connect(self.RunButtonEvent)
        
        ImageLayout = QVBoxLayout()
        ImageLayout.addWidget(NameLabelImagePath)
        ImageLayout.addWidget(SelectImageButton)       
        ImageLayout.addWidget(self.EditImagePath)
        
        ImageLayout.addSpacing(50)
        ImageLayout.addWidget(RunButton)

        ImageLayout.addStretch(1)
        ImageTab.setLayout(ImageLayout)

        InfoTab = QTabWidget()
        InfoTab.setMinimumSize(300, 400)
        InfoTab.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
        InfoTab.addTab(ImageTab, "&Image")
        InfoTab.addTab(VideoTab, "&Video")

        self.InfoGroupTab = QGroupBox()
        TabLayout = QVBoxLayout()
        TabLayout.addWidget(InfoTab)
        self.InfoGroupTab.setLayout(TabLayout)

    def createInfoGroupBox(self):
        self.InfoGroupBox = QTableWidget(15, 2)    
        self.InfoGroupBox.setMinimumSize(600, 400) 
        self.InfoGroupBox.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
        self.InfoGroupBox.setColumnWidth(0, 100)
        self.InfoGroupBox.setColumnWidth(1, 400)
        self.InfoGroupBox.setHorizontalHeaderLabels(["Title", "Value"])

    def createToolBar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        NameLabelCategoryPath = QLabel('Category: ', self)
        NameLabelCategoryPath.setFont(self.TEXT_FONT)

        self.SelectCategoryComboBox = QComboBox()
        self.SelectCategoryComboBox.addItems(self.dictCategory.keys())

        NameLabelCameraSelector = QLabel('Camera: ', self)
        NameLabelCameraSelector.setFont(self.TEXT_FONT)

        self.CameraSelector = QComboBox()
        self.CameraSelector.addItems([camera.description() for camera in self.AvailableCameras])       

        toolbar.setStyleSheet("background : white;")
        toolbar.addWidget(NameLabelCategoryPath)
        toolbar.addWidget(self.SelectCategoryComboBox)
        toolbar.addWidget(NameLabelCameraSelector)
        toolbar.addWidget(self.CameraSelector)

        # self.CameraSelector.currentIndexChanged.connect(self.SelectCamera)

    def SelectCamera(self, i):
        self.closeEvent()
        self.camera_num = self.AvailableCameras[i]
        self.start()

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        QApplication.setPalette(self.originalPalette)

    def SelectFileName(self):
        self.SelectPath, _ = QFileDialog.getOpenFileName(self, 'Select file', '.', "All Files (*);;json Files (*.json);;Image Files (*.jpg)")
        openfile_type = self.SelectPath.split(".")[-1]

        if(openfile_type in self.ImgFile):
            self.ImageFileName = self.SelectPath
            self.EditImagePath.setText(self.ImageFileName)

    def PostProcess(self, process, result, dict_json):
        print("process: ", process)
        if(process == "CCCD VN"):
            return GetData.CCCD_VN_postprocess(result, dict_json)
        if(process == "Driver License"):
            return GetData.DriverLicense_postprocess(result, dict_json)

    def RunButtonEvent(self):
        self.InfoGroupBox.clear()
        self.GetCategoryForm()
        
        img = cv2.imread(self.ImageFileName)
        self.GetInfoFromImage(img, saveCapture = False)
        
    def CaptureButtonEvent(self):
        self.InfoGroupBox.clear()
        self.GetCategoryForm()

        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        ret, frame = self.cap.read()
        self.GetInfoFromImage(frame, saveCapture = True)

    def GetInfoFromImage(self, Image, saveCapture):
        reader = easyocr.Reader(['vi'])
        
        text_results = reader.readtext(Image, beamWidth= 5, text_threshold = 0.7, low_text = 0.4, 
                link_threshold = 0.4, ycenter_ths = 0.5, height_ths = 0.5,
                 width_ths = 0.5, y_ths = 0.5, x_ths = 1.0)        
        # box_results, _ = reader.detect(Image)
        for r in text_results:            
            print(r[0:2])

        dictInfomation = self.PostProcess(self.SelectCategoryComboBox.currentText(), text_results, self.dict_json)

        self.add_Infomation(self.InfoGroupBox, dictInfomation)

        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        FileNameResult = dictInfomation["Number"]["value"] + timestamp
        PathResultJson = "OutPut/jsonfile/" + FileNameResult + ".json"
        PathImageCapture = "OutPut/captureImages/" + FileNameResult + ".jpg"

        with open (PathResultJson, 'w', encoding='utf-8') as f:
            jsonObject = json.dumps(dictInfomation, indent=4, cls=NpEncoder, ensure_ascii = False)      
            f.write(jsonObject)
            print("Save Json File Done")

        if(saveCapture):
            cv2.imwrite(PathImageCapture, Image)

    def GetCategoryForm(self):
        try:
            self.LoadPathJsonForm()
            f= open(self.CategoryFileName)
            self.dict_json = json.load(f)
        except:
            print("Error open file Category json")

    def LoadJsonConfigFile(self):
        try:
            f= open("FormJson/configMapForm.json")
            self.dictCategory = json.load(f)
        except:
            print("Error Open config file")

    def LoadPathJsonForm(self):
        JsonForm = self.SelectCategoryComboBox.currentText()
        try:
            self.CategoryFileName = self.dictCategory[JsonForm]
            print("CategoryFileName: ", self.CategoryFileName)
        except:
            print("Error load file Json Form")

    def add_Infomation(self, tableWidget, dictData):
        currentRow = -1
        for key in dictData:
            currentRow += 1
            if currentRow > len(dictData) - 1:
                tableWidget.insertRow(tableWidget.rowCount())

            tableWidget.setItem(currentRow, 0, QTableWidgetItem(key))
            if(isinstance(dictData[key], dict)):
                tableWidget.setItem(currentRow, 1, QTableWidgetItem(dictData[key]["value"]))
            else:
                tableWidget.setItem(currentRow, 1, QTableWidgetItem(dictData[key]))
        tableWidget.resizeColumnsToContents()

    def PostProcess(self, process, result, dict_json):
        print("process: ", process)
        if(process == "CCCD VN"):
            print("result")
            print(result)
            print("dict_json")
            print(dict_json)
            return GetData.CCCD_VN_postprocess(result, dict_json)
        if(process == "Driver License"):
            return GetData.DriverLicense_postprocess(result, dict_json)

    # Start image capture & display
    def start(self):
        # Timer to trigger display
        self.timer.timeout.connect(lambda: self.show_image(self.image_queue, self.DisplayVideo, self.DISP_SCALE))
        self.timer.start(self.DISP_MSEC)         
        self.capture_thread = threading.Thread(target=self.grab_images, args=(self.camera_num, self.image_queue))
        self.capture_thread.start()         # Thread to grab images

    # Fetch camera image from queue, and display it
    def show_image(self, imageq, display, scale):
        if not imageq.empty():
            image = imageq.get()
            if image is not None and len(image) > 0:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.display_image(img, display, scale)

    # Display an image, reduce size if required
    def display_image(self, img, display, scale=1):
        disp_size = img.shape[1]//scale, img.shape[0]//scale
        disp_bpl = disp_size[0] * 3
        if scale > 1:
            img = cv2.resize(img, disp_size, 
                             interpolation=cv2.INTER_CUBIC)
        qimg = QImage(img.data, disp_size[0], disp_size[1], 
                      disp_bpl, self.IMG_FORMAT)
        display.setImage(qimg)

    # Window is closing: stop video capture
    def closeEvent(self):
        self.timer.stop()
        global capturing
        capturing = False
        print("Change Camera !")
        self.capture_thread.join()
        print("Change Camera done!")

    # Grab images from the camera (separate thread)
    def grab_images(self, cam_num, queue):
        self.cap = cv2.VideoCapture(cam_num-1 + self.CAP_API)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.IMG_SIZE[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.IMG_SIZE[1])
        if self.EXPOSURE:
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            self.cap.set(cv2.CAP_PROP_EXPOSURE, self.EXPOSURE)
        else:
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        while self.capturing:
            if self.cap.grab():
                retval, image = self.cap.retrieve(0)
                if image is not None and queue.qsize() < 2:
                    queue.put(image)
                else:
                    time.sleep(self.DISP_MSEC / 1000.0)
            else:
                print("Error: can't grab camera image")
                break
        self.cap.release()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = AppWindow()
    win.show()
    win.setWindowTitle(VERSION)
    win.start()
    sys.exit(app.exec_())

#EOF