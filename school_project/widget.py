# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.NonModal)
        Form.resize(560, 360)
        Form.setMinimumSize(QtCore.QSize(480, 320))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/background image/pictureresult.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        Form.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(Form)
        self.centralwidget.setObjectName("centralwidget")
        if isinstance(Form, QtWidgets.QMainWindow):
            Form.setCentralWidget(self.centralwidget)
            layout_parent = self.centralwidget
            style_target = Form
        else:
            layout_parent = Form
            style_target = Form

        style_target.setStyleSheet("""
QWidget#Form {
    background-color: qlineargradient(
        spread:pad, x1:0.091, y1:0.102, x2:0.991, y2:0.997,
        stop:0 rgba(209, 107, 165, 255),
        stop:1 rgba(255, 255, 255, 255)
    );
}
QWidget#centralwidget {
    background-color: qlineargradient(
        spread:pad, x1:0.091, y1:0.102, x2:0.991, y2:0.997,
        stop:0 rgba(209, 107, 165, 255),
        stop:1 rgba(255, 255, 255, 255)
    );
}
QLabel#label {
    color: white;
    font: 700 22pt "Microsoft JhengHei UI";
}
QListWidget {
    border: 1px solid rgba(255, 255, 255, 160);
    border-radius: 10px;
    background: rgba(255, 255, 255, 210);
    padding: 6px;
    font: 10pt "Microsoft JhengHei UI";
}
QPushButton {
    border: 0;
    border-radius: 10px;
    background-color: rgb(170, 255, 255);
    min-height: 34px;
    padding: 6px 12px;
    font: 10pt "Microsoft JhengHei UI";
}
QPushButton#pushButton_3 {
    border-radius: 14px;
    font: 700 11pt "Microsoft JhengHei UI";
    min-height: 54px;
}
""")

        self.verticalLayout = QtWidgets.QVBoxLayout(layout_parent)
        self.verticalLayout.setContentsMargins(24, 20, 24, 20)
        self.verticalLayout.setSpacing(14)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label = QtWidgets.QLabel(layout_parent)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.listWidget = QtWidgets.QListWidget(layout_parent)
        self.listWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listWidget.setMovement(QtWidgets.QListView.Static)
        self.listWidget.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget.setWordWrap(False)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget, 1)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setSpacing(10)
        self.buttonLayout.setObjectName("buttonLayout")

        self.pushButton = QtWidgets.QPushButton(layout_parent)
        self.pushButton.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.pushButton.setObjectName("pushButton")
        self.buttonLayout.addWidget(self.pushButton)

        self.pushButton_2 = QtWidgets.QPushButton(layout_parent)
        self.pushButton_2.setObjectName("pushButton_2")
        self.buttonLayout.addWidget(self.pushButton_2)

        self.pushButton_4 = QtWidgets.QPushButton(layout_parent)
        self.pushButton_4.setObjectName("pushButton_4")
        self.buttonLayout.addWidget(self.pushButton_4)

        self.pushButton_3 = QtWidgets.QPushButton(layout_parent)
        self.pushButton_3.setEnabled(True)
        self.pushButton_3.setCheckable(False)
        self.pushButton_3.setDefault(False)
        self.pushButton_3.setFlat(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.buttonLayout.addWidget(self.pushButton_3)

        self.verticalLayout.addLayout(self.buttonLayout)

        self.progressBar = QtWidgets.QProgressBar(layout_parent)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "相似系列圖片自動整理系統 1.4"))
        self.label.setText(_translate("Form", "選擇的資料夾："))
        self.listWidget.setStatusTip(_translate("Form", "path"))
        self.listWidget.setSortingEnabled(False)
        self.pushButton_3.setToolTip(_translate("Form", "進入主畫面 (4)"))
        self.pushButton_3.setStatusTip(_translate("Form", "進入主畫面"))
        self.pushButton_3.setText(_translate("Form", "進入主畫面"))
        self.pushButton_3.setShortcut(_translate("Form", "4"))
        self.pushButton.setToolTip(_translate("Form", "選擇資料夾 (1)"))
        self.pushButton.setStatusTip(_translate("Form", "選擇資料夾"))
        self.pushButton.setText(_translate("Form", "選擇資料夾"))
        self.pushButton.setShortcut(_translate("Form", "1"))
        self.pushButton_2.setToolTip(_translate("Form", "開始掃描 (2)"))
        self.pushButton_2.setStatusTip(_translate("Form", "開始掃描"))
        self.pushButton_2.setText(_translate("Form", "開始掃描"))
        self.pushButton_2.setShortcut(_translate("Form", "2"))
        self.pushButton_4.setToolTip(_translate("Form", "取消掃描 (3)"))
        self.pushButton_4.setStatusTip(_translate("Form", "取消掃描"))
        self.pushButton_4.setText(_translate("Form", "取消掃描"))
        self.pushButton_4.setShortcut(_translate("Form", "3"))


import image_rc


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
