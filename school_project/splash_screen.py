# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        SplashScreen.setObjectName("SplashScreen")
        SplashScreen.resize(460, 300)
        SplashScreen.setMinimumSize(QtCore.QSize(420, 280))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/background image/pictureresult.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        SplashScreen.setWindowIcon(icon)

        self.centralwidget = QtWidgets.QWidget(SplashScreen)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setStyleSheet("""
QFrame {
    background-color: rgb(56, 58, 89);
    color: rgb(220, 220, 220);
    border-radius: 10px;
}
""")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.frameLayout = QtWidgets.QVBoxLayout(self.frame)
        self.frameLayout.setContentsMargins(24, 34, 24, 28)
        self.frameLayout.setSpacing(18)
        self.frameLayout.setObjectName("frameLayout")

        self.label_tittle = QtWidgets.QLabel(self.frame)
        self.label_tittle.setStyleSheet("color: rgb(254, 121, 199);")
        self.label_tittle.setAlignment(QtCore.Qt.AlignCenter)
        self.label_tittle.setWordWrap(True)
        self.label_tittle.setObjectName("label_tittle")
        self.frameLayout.addWidget(self.label_tittle)

        self.label_description = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Microsoft JhengHei UI")
        font.setPointSize(14)
        self.label_description.setFont(font)
        self.label_description.setStyleSheet("color: rgb(190, 198, 232);")
        self.label_description.setAlignment(QtCore.Qt.AlignCenter)
        self.label_description.setObjectName("label_description")
        self.frameLayout.addWidget(self.label_description)

        self.progressBar = QtWidgets.QProgressBar(self.frame)
        self.progressBar.setStyleSheet("""
QProgressBar {
    background-color: rgb(98, 114, 164);
    color: rgb(240, 240, 240);
    border-style: none;
    border-radius: 10px;
    text-align: center;
}
QProgressBar::chunk {
    border-radius: 10px;
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523,
        stop:0 rgba(254, 121, 199, 255),
        stop:1 rgba(170, 85, 255, 255)
    );
}
""")
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.frameLayout.addWidget(self.progressBar)

        self.label_loading = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Microsoft JhengHei UI")
        font.setPointSize(12)
        self.label_loading.setFont(font)
        self.label_loading.setStyleSheet("color: rgb(190, 198, 232);")
        self.label_loading.setAlignment(QtCore.Qt.AlignCenter)
        self.label_loading.setObjectName("label_loading")
        self.frameLayout.addWidget(self.label_loading)

        self.verticalLayout.addWidget(self.frame)
        SplashScreen.setCentralWidget(self.centralwidget)

        self.retranslateUi(SplashScreen)
        QtCore.QMetaObject.connectSlotsByName(SplashScreen)

    def retranslateUi(self, SplashScreen):
        _translate = QtCore.QCoreApplication.translate
        SplashScreen.setWindowTitle(_translate("SplashScreen", "相似系列圖片自動整理系統"))
        self.label_tittle.setText(_translate("SplashScreen", "<html><head/><body><p><span style=\" font-size:24pt; font-weight:600;\">相似系列圖片自動整理系統</span></p></body></html>"))
        self.label_description.setText(_translate("SplashScreen", "<strong>照片匹配</strong> 電腦 app"))
        self.label_loading.setText(_translate("SplashScreen", "載入中....."))


import image_rc


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    SplashScreen = QtWidgets.QMainWindow()
    ui = Ui_SplashScreen()
    ui.setupUi(SplashScreen)
    SplashScreen.show()
    sys.exit(app.exec_())
