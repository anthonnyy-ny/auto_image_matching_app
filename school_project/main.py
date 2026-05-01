# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 16:16:51 2022

@author: User
"""








from controller import Form_controller
from splash_screen import Ui_SplashScreen



import sys
import class_list
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtGui import *
#import timer
#import platform



class_list = 0

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(self)
        self.ui = MainWindow_controller2()
        self.ui.setupUi(self)

        



class splash_screen_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.progress()
        self.IsStore=0
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
       ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

        # CHANGE DESCRIPTION

        # Initial Text
        self.ui.label_description.setText("<strong>歡迎使用</strong> 圖片整理系統")

        # Change Texts
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>讀取</strong> 圖片資料"))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.label_description.setText("<strong>載入</strong> 使用介面"))


        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##

    ## ==> APP FUNCTIONS
    ########################################################################
    def progress(self):

        global class_list

        #SET VALUE TO PROGRESS BAR
        self.ui.progressBar.setValue(class_list)

       #  CLOSE SPLASH SCREE AND OPEN APP
        if class_list > 100:
            # STOP TIMER
            self.timer.stop()
            
            #OPEN　
            
            self.main = Form_controller()
            self.main.show()
            

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        class_list += 1




if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    ui = splash_screen_controller()
   # ui.show()
    sys.exit(app.exec_())
    
    #from controller2 import MainWindow_controller2





#from controller import Form_controller
#from splash_screen_main import splash_screen_controller

#import class_list

#def main():
   # import sys
  #  app2 = QtWidgets.QApplication(sys.argv)
  #  ui = splash_screen_controller()
#    ui.show()
  #  sys.exit(app2.exec_())
   # import sys
   # app = QtWidgets.QApplication(sys.argv)
    #window = Form_controller()
   # window.show()
  #  sys.exit(app.exec_())

    
#if __name__ == '__main__':
   # class_list.create_global()
  #  main()
