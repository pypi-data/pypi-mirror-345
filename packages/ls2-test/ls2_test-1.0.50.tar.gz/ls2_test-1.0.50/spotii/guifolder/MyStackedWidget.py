import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import time
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
#from SlotPage import SlotPage
from slot.scan import _Scan
from slot.empty import _Empty
from slot.detecting import _Detecting
from slot.warning import _Warning
from slot.positive import _Positive
from slot.negative import _Negative
from slot.invalid import _Invalid
from slot.flip import _Flip
from slot.invalid_qr import _Invalid_qr
from test_handler.cassette_polling import CassettePolling
from test_handler.test_chip_handler import getDevice
import title_rc
from emit_thread import SignalThread
#from main_paras import mainChannelNotify, getDetectionMode
from main_paras import mainChannelNotify, getDetectionMode, setOperation
from main_paras import queueForGui, queueForResult, queueForCom
#from test_handler.cassette_polling import CassettePolling
from define import *
import main_paras


class PageResponse(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)



class MyStackedWidget(QtWidgets.QStackedWidget):
    def __init__(self,parent=None):
        super(MyStackedWidget, self).__init__(parent)
        self.button_hooks=[None,None,None,None,None,None,self.scanHook,self.flipHook,self.invalidQrHook]
        
        self.slotBasic = [
           (None,                self.empty,),
           (None,                self.warning,),
           (None,                self.detecting,),
           (None,                self.positive,),
           (None,                self.negative,),
           (None,                self.invalid,),
           (self.scanHook,       self.scan,),
           (self.flipHook,       self.flip,),
           (self.invalidQrHook,  self.invalid_qr,),
            ]
        self.slot_no = 0
        self.cassetteId=""
        self.timeLeft = TIMER_DURATION
        self.timeIncreasing = 0
        self.myTimer = QtCore.QTimer()
        self.myTimer.timeout.connect(self.timer_timeout)
        
        self.ready=False
        self.i2c=None
        self.camera=None
        self.function=None
#         self.pageResponse = PageResponse()
#         self.pageResponse.signal.connect(self.emitHook)
        self.pageParking = SignalThread()
        self.pollingTimer=QtCore.QTimer()
        self.pollingTimer.timeout.connect(self.polling_repeat)
        
        self.cassetteIn=False
        
        loadUi(os.path.join(currentdir,'myStackedWidget.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.resize(96, 224)
        
        
    def polling_repeat(self):
        self.pageParking.signal.emit(time.time())
        #print(self.slot_no, time.time(),self.pageParking.signal)
        self.pollingTimer.start(1000)
        
        
    def empty(self, item):
        print(self.slot_no, 'empty', item)
    def warning(self, item):
        print(self.slot_no, 'warning', item)
    def detecting(self, item):
        print(self.slot_no, 'detecting', item)
    def positive(self, item):
        print(self.slot_no, 'positive', item)
    def negative(self, item):
        print(self.slot_no, 'negative', item)
    def invalid(self, item):
        print(self.slot_no, 'invalid', item)
    def scan(self, item):
        print(self.slot_no, 'scan', item)
    def flip(self, item):
        print(self.slot_no, 'flip', item)
    def invalid_qr(self, item):
        print(self.slot_no, 'invalid_qr', item)
        
    def scanHook(self):
        print('scanHook', self.slot_no)
        if not main_paras.signedIn():
            main_paras.queueForGui.put([SIGN_IN_FIRST_INDEX,'','',''])
            return
        setOperation(self.slot_no ,MANUAL_OPERATION_SCAN)
    def flipHook(self):
        print('flipHook', self.slot_no)
        setOperation(self.slot_no ,MANUAL_OPERATION_START_TESTING)
    def invalidQrHook(self):
        print('invalidQrHook', self.slot_no)
        setOperation(self.slot_no ,MANUAL_OPERATION_START)

    def setSlotNo(self,number):
        try:
            assert(number >= 0 and number <=4), "Wrong slot number"
            self.slot_no = number
            for page in range(0, len(self.slotBasic)):
                self.setCurrentIndex(page)
                self.currentWidget().setDetail(self.slot_no)
                self.currentWidget().buttonHook(self.slotBasic[page][0])
            self.ready=True
            
            self.setCurrentIndex(0)
            #self.pollingTimer.start()
            while True:
                ready, device = getDevice(self.slot_no)
                if ready:
                    break
                time.sleep(0.2)
            #print('slot_',self.slot_no,'device ready', ready, device)
            if device[1] != INVALID_DEVICE_INDEX:
                self.cassettePolling=CassettePolling(self.slot_no, device[0], device[1], queueForResult, queueForCom, self.pollingCallback)
                self.cassettePolling.start()
            else:
                self.setCurrentIndex(SLOT_STATUS_WARNING)
                page=self.currentWidget()
                page.id.setText('Camera fail')
                
            
        except Exception as error:
            print(error)
        except AssertionError as e:
            raise Exception( e.args )

    def config(self):
        try:
            #self.currentChanged.connect(self.onChanged)
            pass
        except Exception as error:
            print(error)

    def setStatus(self, status_index, cassette, time=None):
        try:
            #print("before setting widget index:",self.currentIndex(), status_index)
            if self.currentIndex() == SLOT_STATUS_EMPTY:
                if status_index!= SLOT_STATUS_DETECTING:
                    return
            
            self.cassetteId=cassette
            self.setCurrentIndex(status_index)
            #print("after  setting widget index:",self.currentIndex())
            page=self.currentWidget()
            try:        ## some pages don't have id
                page.id.setText(self.cassetteId)
                if self.cassetteId.startswith('M'):
                    page.target_name.setText('Urine test')
                else:
                    page.target_name.setText('SARS-CoV-2')
                    
            except:
                pass
            if(time!=None):
                page.timer.setText(time) ## 1 for counting down timer
            else:
                self.myTimer.stop()
        except Exception as e:
            print (e)
    def setCassetteID(self,c_id):
        self.cassetteId =c_id
    def detecting_(self, cassette):
        try:
            self.cassetteId=cassette
            self.timeLeft = TIMER_DURATION
            self.timeIncreasing = 0
            self.myTimer.start(1000)
            self.showDetecting()
        except Exception as e:
            print(e)

    def timer_timeout(self):
        try:
            self.timeLeft -= 1
            self.timeIncreasing += 1
            self.showDetecting()        
            if self.timeLeft == 0:
                self.detection_timeout()
                self.timeIncreasing = 0
                self.myTimer.stop()
        except Exception as e:
            print(e)
        
    def showDetecting(self):
        try:
            self.setStatus(SLOT_STATUS_DETECTING, self.cassetteId, time.strftime('%-M:%S', time.gmtime(self.timeIncreasing)))
        except Exception as e:
            print(e)
    def detection_timeout(self):
        try:
            self.setStatus(SLOT_STATUS_WARNING, self.cassetteId)
        except Exception as e:
            print(e)

    def onChanged(self, index):
        if self.ready :
            try:
                self.pageParking.signal.disconnect()
            except Exception:
                pass
            self.pageParking.signal.connect(self.slotBasic[index][1])
            
    def totalPage(self):
        return len(self.slotBasic)
    def pollingCallback (self, cassetteIn):
        self.cassetteIn = cassetteIn
    def closeNow(self):
        self.cassettePolling.notify(CLOSE_NOW)
        self.cassettePolling.join()
#        print("slot_%d is closed" % (self.slot_no))
        
        
#     def closeEvent(self,event):
#         print("slot %d is closing" % (self.slot_no))
#         self.cassettePolling.notify(CLOSE_NOW)
#         self.cassettePolling.join()
#         print("slot %d is closed" % (self.slot_no))

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
    window=MyStackedWidget()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
