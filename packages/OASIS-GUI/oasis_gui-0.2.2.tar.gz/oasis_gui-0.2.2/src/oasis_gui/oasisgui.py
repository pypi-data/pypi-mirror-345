'''
 OASIS-Gui.py
 
	Main class of the OASIS-GUI used for interacting with OASIS devices

  Copyright (c) 2025 Oliver Zobel - MIT License

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
  to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
  IN THE SOFTWARE.
  
 '''

import sys
import serial
import time
import os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.uic import loadUi
from oasis_gui.ui.OASISUI import Ui_MainWindow

from oasis_gui.src.searchDevices import searchDevices
from oasis_gui.src.sampleHandler import sampleHandler
from oasis_gui.src.dataHandler import dataHandler
from oasis_gui.src.convertSample import convertSample

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton, True)

if sys.platform.startswith('win'):
    import ctypes
    myappid = 'OASIS-GUI'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

DeviceSearch = searchDevices()
SampleHandler = sampleHandler()

app = QApplication(sys.argv)

# set app icon    
app_icon = QtGui.QIcon()
app_icon.addFile(':/Icons/resources/icons/16x16.png', QtCore.QSize(16,16))
app_icon.addFile(':/Icons/resources/icons/24x24.png', QtCore.QSize(24,24))
app_icon.addFile(':/Icons/resources/icons/32x32.png', QtCore.QSize(32,32))
app_icon.addFile(':/Icons/resources/icons/48x48.png', QtCore.QSize(48,48))
app_icon.addFile(':/Icons/resources/icons/64x64.png', QtCore.QSize(64,64))
app_icon.addFile(':/Icons/resources/icons/256x256.png', QtCore.QSize(256,256))
app.setWindowIcon(app_icon)

def run():
    win = Window()
    win.show()
    sys.exit(app.exec())

class WorkerDeviceSearch(QObject):
    
    finished = pyqtSignal()
    printLogSignal = pyqtSignal(str)
    
    def __init__(self, DeviceSearch):
        super(WorkerDeviceSearch, self).__init__()
        self.DeviceSearch = DeviceSearch

    def run(self):
        self.DeviceSearch.SerialSearch(self.printLogSignal)
        self.finished.emit()
        
class WorkerSerialSample(QObject):
    
    finished = pyqtSignal()
    printLogSignal = pyqtSignal(str)
    sampleAborted = pyqtSignal()
    sampleProgress = pyqtSignal(int)
    
    def __init__(self, SampleHandler, DataHandler):
        super(WorkerSerialSample, self).__init__()
        self.SampleHandler = SampleHandler
        self.DataHandler = DataHandler

    def newSample(self):
        self.SampleHandler.SampleSerial(self.printLogSignal, self.sampleAborted, self.sampleProgress, self.DataHandler)
        self.finished.emit()
        
    def resendPreviousSample(self):
        self.SampleHandler.resendSampleSerial(self.printLogSignal, self.sampleAborted, self.sampleProgress, self.DataHandler)
        self.finished.emit()
        
class WorkerConvertSample(QObject):
    
    finished = pyqtSignal()
    printLogSignal = pyqtSignal(str)

    def __init__(self, filename, metaContentDict, DataHandler):
        super().__init__()
        self.filename = filename
        self.DataHandler = DataHandler
        self.metaContentDict = metaContentDict

    def run(self):
        convertSample.convertFromMeta(self.filename, self.metaContentDict, self.printLogSignal, self.DataHandler)
        self.finished.emit()

class Window(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.DataHandler = dataHandler()
        self.setupUi(self)
        self.connectSignalsSlots()
        self.progressBar_2.setVisible(False)
        self.label_19.setVisible(False)
        self.movie = QMovie(":/Misc/resources/spin.gif")
        self.label_19.setMovie(self.movie)
        self.movie.start()
        self.DeviceLocked = False
        self.RelockDevice = False
        self.Search_Devices()

    def connectSignalsSlots(self):
        self.actionAbout.triggered.connect(self.About)
        self.actionSearch_Devices.triggered.connect(self.Search_Devices)
        self.actionSerial_Sample.triggered.connect(self.Serial_Sample)
        self.actionResendData.triggered.connect(self.Resend_Sample)
        self.actionDevice_Selected_Changed.triggered.connect(self.Update_Device)
        self.actionRange_Channel1_Changed.triggered.connect(self.Update_Range)
        self.actionshow_Previous_Data.triggered.connect(self.Show_Previous_Data)
        self.actionsave_Previous_Data.triggered.connect(self.Save_Previous_Data)
        self.label_21.mousePressEvent = self.LockDevice
        self.actionVoltageRangeAll.triggered.connect(self.Update_VoltageRangesAll)
        self.actionConvert_OASIS_Sample.triggered.connect(self.Convert_Sample)

    def About(self):
        dialog = AboutDialog(self)
        dialog.exec()
        
    def Update_Device(self):
        DeviceSearch.UpdateSelectedDevice(self)
    
    def Update_VoltageRangesAll(self):
        DeviceSearch.UpdateAllVoltageRanges(self)
        
    def Update_Range(self):
        if DeviceSearch.Devices and len(DeviceSearch.Devices[self.comboBox.currentIndex()][1])==7:
            if(DeviceSearch.Devices[self.comboBox.currentIndex()][1][2]=="16"):
                self.comboBox_3.setCurrentIndex(self.comboBox_2.currentIndex())
                self.comboBox_4.setCurrentIndex(self.comboBox_2.currentIndex())
                self.comboBox_5.setCurrentIndex(self.comboBox_2.currentIndex())
        
    def Search_Devices(self):
        # Lock & Update GUI
        self.pushButton.setEnabled(False)
        self.tabWidget.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_7.setEnabled(False)
        self.textEdit.clear()
        self.label_19.setVisible(True)
        DeviceSearch.Devices = []
        DeviceSearch.UpdateDeviceList(self)
        DeviceSearch.UpdateSelectedDevice(self)
        self.comboBox.setItemText(0, "Searching Devices...")
        
        # Setup Worker & Thread
        self.thread = QThread()
        self.workerDeviceSearch = WorkerDeviceSearch(DeviceSearch)
        self.workerDeviceSearch.moveToThread(self.thread)
        
        # Connect Signals
        self.workerDeviceSearch.finished.connect(self.thread.quit)
        self.workerDeviceSearch.printLogSignal.connect(self.printLog)
        self.thread.started.connect(self.workerDeviceSearch.run)
        self.thread.finished.connect(self.Search_Devices_PostProcess)
        
        self.thread.start()
        
    def Search_Devices_PostProcess(self):
        self.pushButton.setEnabled(True)
        DeviceSearch.UpdateDeviceList(self)
        DeviceSearch.UpdateSelectedDevice(self)
        self.label_19.setVisible(False)
        
    def printLog(self, string):
        self.textEdit.insertPlainText(string)
        self.textEdit.ensureCursorVisible()
        
    def Serial_Sample(self):
        # Lock & Update GUI
        self.tabWidget.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.progressBar.setValue(0)
        self.progressBar_2.setVisible(False)
        self.groupBox_5.setEnabled(False)
        self.sampleError = False
        self.LastSampleDevice = DeviceSearch.Devices[self.comboBox.currentIndex()][1][5]

        # Release Serial lock
        if self.DeviceLocked:
            try:
                self.LockSerial.close()
                time.sleep(0.5)
            except:
                pass
            self.RelockDevice = True
            self.DeviceLocked = False

        # Get Acquisition Paramters from user input
        SampleHandler.getAcquisitionParameters(self, DeviceSearch.Devices[self.comboBox.currentIndex()])
        
        # Setup Worker & Thread
        self.thread = QThread()
        self.workerSerialSample = WorkerSerialSample(SampleHandler, self.DataHandler)
        self.workerSerialSample.moveToThread(self.thread)
        
        # Connect Signals
        self.workerSerialSample.finished.connect(self.thread.quit)
        self.workerSerialSample.printLogSignal.connect(self.printLog)
        self.workerSerialSample.sampleAborted.connect(self.abortSample)
        self.workerSerialSample.sampleProgress.connect(self.updateProgressBar)
        self.thread.started.connect(self.workerSerialSample.newSample)
        self.thread.finished.connect(self.Serial_Sample_PostProcess)
        
        self.thread.start()
        
    def Resend_Sample(self):
        # Lock & Update GUI
        self.tabWidget.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.progressBar.setValue(0)
        self.progressBar_2.setVisible(False)
        self.groupBox_5.setEnabled(False)
        self.sampleError = False
        self.LastSampleDevice = DeviceSearch.Devices[self.comboBox.currentIndex()][1][5]

        # Release Serial lock
        if self.DeviceLocked:
            try:
                self.LockSerial.close()
                time.sleep(0.5)
            except:
                pass
            self.RelockDevice = True
            self.DeviceLocked = False
        
        # Setup Worker & Thread
        self.thread = QThread()
        self.workerSerialSample = WorkerSerialSample(SampleHandler, self.DataHandler)
        self.workerSerialSample.moveToThread(self.thread)
        
        # Connect Signals
        self.workerSerialSample.finished.connect(self.thread.quit)
        self.workerSerialSample.printLogSignal.connect(self.printLog)
        self.workerSerialSample.sampleAborted.connect(self.abortSample)
        self.workerSerialSample.sampleProgress.connect(self.updateProgressBar)
        self.thread.started.connect(self.workerSerialSample.resendPreviousSample)
        self.thread.finished.connect(self.Serial_Sample_PostProcess)
        
        self.thread.start()

    def abortSample(self):
        self.sampleError = True
        self.progressBar_2.setVisible(True)
        self.progressBar.setValue(0)
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.tabWidget.setEnabled(True)
        
    def Convert_Sample(self):
        filename = QFileDialog.getOpenFileName(caption='Select *.OASISmeta file for sample conversion',filter='OASIS Meta File (*.OASISmeta)')[0]
        
        if not filename:
            return
        
        # Load meta data from selected file
        metaContent = open(filename).read().split(';')[:-1]
        metaContentDict = dict(metaContentSplitObj.split(',',1) for metaContentSplitObj in metaContent)
        triggered_sample = (float(metaContentDict.get('trigg_level')) !=0)
        
        # Check for raw files
        filenameraw = f'{filename[:-4]}raw'
        try:
            OASISRawData = open(filenameraw, "rb").read()
        except:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(f"No such file: {filenameraw.split('/')[-1]}")
            msg_box.setText(f"Could not find the raw measurement file '{filenameraw.split('/')[-1]}'")
            msg_box.exec()
            return
        
        if triggered_sample:
            filenamerawpretrigg = f'{filename[:-10]}_PRE.OASISraw'
            try:
                OASISRawDataPre = open(filenamerawpretrigg, "rb").read()
            except:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle(f"No such file: {filenamerawpretrigg.split('/')[-1]}")
                msg_box.setText(f"Could not find the raw pre-trigger measurement file '{filenamerawpretrigg.split('/')[-1]}'")
                msg_box.exec()
                return
        
        # Show processing dialog
        dialog = WaitDialog(self)
        dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint )
        dialog.open()
        
        self.thread = QThread()
        self.workerConvertSample = WorkerConvertSample(filename, metaContentDict, self.DataHandler)
        self.workerConvertSample.moveToThread(self.thread)
        self.workerConvertSample.printLogSignal.connect(self.printLog)
        self.thread.started.connect(self.workerConvertSample.run)
        
        self.workerConvertSample.finished.connect(self.Convert_Sample_PostProcess)
        self.workerConvertSample.finished.connect(dialog.close)
        self.workerConvertSample.finished.connect(self.thread.quit)
        self.workerConvertSample.finished.connect(self.workerConvertSample.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
    
        self.thread.start()
        
    def Convert_Sample_PostProcess(self):
        if self.checkBox_4.isChecked():
            self.Show_Previous_Data()
        if self.checkBox_5.isChecked():
            self.Save_Previous_Data()
        self.tabWidget.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.groupBox.setEnabled(False)
        self.groupBox_2.setEnabled(False)
        self.groupBox_4.setEnabled(False)
        self.groupBox_7.setEnabled(False)
        self.groupBox_3.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)
        
    def Serial_Sample_PostProcess(self):
        if self.checkBox_4.isChecked() and not self.sampleError:
            self.Show_Previous_Data()
        if self.checkBox_5.isChecked() and not self.sampleError:
            self.Save_Previous_Data()
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        self.pushButton_7.setEnabled(True)
        if DeviceSearch.Devices[self.comboBox.currentIndex()][1][4]:
            self.groupBox_5.setEnabled(True)
        if self.RelockDevice:
            self.LockDevice("JA")
        if not self.DeviceLocked:
            self.comboBox.setEnabled(True)
        self.tabWidget.setEnabled(True)
        
    def Show_Previous_Data(self):
        self.DataHandler.plotData()
    
    def Save_Previous_Data(self):
        self.DataHandler.saveData(self)

    def LockDevice(self, garbage):
        self.DeviceLocked = not self.DeviceLocked
        if self.DeviceLocked:
            self.textEdit.append(f"[OASIS-GUI]: Locking {self.comboBox.currentText()}\n")
            try:
                self.LockSerial = serial.Serial(port=DeviceSearch.Devices[self.comboBox.currentIndex()][0], baudrate=DeviceSearch.serialSpeed, timeout=2)
            except (OSError, serial.SerialException):
                self.textEdit.append("[OASIS-GUI]: DEVICE ERROR! Could not lock device.\n")
                self.DeviceLocked = False

            self.comboBox.setEnabled(False)
            self.label_21.setPixmap(QtGui.QPixmap(":/Misc/resources/lock.png"))
        else:
            try:
                self.LockSerial.close()
            except:
                pass

        if not self.DeviceLocked:
            self.textEdit.append(f"[OASIS-GUI]: Unlocking {self.comboBox.currentText()}\n")
            self.comboBox.setEnabled(True)
            self.label_21.setPixmap(QtGui.QPixmap(":/Misc/resources/unlock.png"))

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.dirname(os.path.abspath(__file__)) + "/ui/OASISGui_About.ui", self)
        
class WaitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.dirname(os.path.abspath(__file__)) + "/ui/OASISGui_processing.ui", self)
        self.movie = QMovie(":/Misc/resources/spin.gif")
        self.spin_label.setMovie(self.movie)
        self.movie.start()