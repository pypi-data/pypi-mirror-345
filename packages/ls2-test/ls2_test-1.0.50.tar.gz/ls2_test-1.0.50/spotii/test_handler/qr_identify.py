import cv2
import numpy as np
from pyzbar import pyzbar
from algorithm import alg
from calibration import crop_rotate, FINAL_WIDTH, FINAL_HEIGHT

def qrCut(image):
    image = alg.balance(image,200)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,1))
    target = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
##    cv2.imshow("thresh", thresh)
##    cv2.imshow("target", target)
##    cv2.waitKey(0)
    return target
BAR_CODE_HIGH = 808

def qrIdentify(original_image):
    try:

        image = qrCut(original_image)
#         cv2.imshow("image", image)
#         cv2.waitKey(0)
        barcode = pyzbar.decode(image)
        print('barcode:',barcode)
        if barcode!=[]:
            (x, y, w, h) = barcode[0].rect
            if y>BAR_CODE_HIGH:   ## Sometimes barcode return height just 1, using BAR_CODE_HIGH to adjust y
                y-=BAR_CODE_HIGH
                
            return(barcode[0].data.decode("utf-8")), x, y
        return None, None, None

    except Exception as e:
        print(e)
        return None, None, None




if __name__ == "__main__":
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
    from PyQt5 import QtCore
    import sys
     
     
    def dialog():
        options = QtWidgets.QFileDialog.Options()
        file , check = QtWidgets.QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","Png, Jpg Files (*.jpg; *.png)", options=options)
        if check:
            image=cv2.imread(file)
  
            print(qrIdentify(image))
     
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(400,400,300,300)
    win.setWindowTitle("CodersLegacy")
      
    button = QPushButton(win)
    button.setText("Press")
    button.clicked.connect(dialog)
    button.move(50,50)
     
    win.show()
    sys.exit(app.exec_())        

