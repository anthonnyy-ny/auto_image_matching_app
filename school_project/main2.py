# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 16:20:56 2022

@author: User
"""

from PyQt6 import QtWidgets

from controller2 import MainWindow_controller2



#main function
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller2()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    
    main()
   