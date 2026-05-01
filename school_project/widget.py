# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from animated_ui import AnimatedBackgroundWidget, GlowButton


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.NonModal)
        Form.resize(760, 520)
        Form.setMinimumSize(QtCore.QSize(640, 460))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/background image/pictureresult.ico"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        Form.setWindowIcon(icon)

        self.centralwidget = AnimatedBackgroundWidget(Form)
        self.centralwidget.setObjectName("centralwidget")
        if isinstance(Form, QtWidgets.QMainWindow):
            Form.setCentralWidget(self.centralwidget)
            layout_parent = self.centralwidget
            style_target = Form
        else:
            layout_parent = Form
            style_target = Form

        style_target.setStyleSheet("""
QWidget#Form, QWidget#centralwidget {
    background: transparent;
}
QFrame#heroFrame {
    border-radius: 16px;
    background-color: rgba(255, 255, 255, 34);
    border: 1px solid rgba(255, 255, 255, 74);
}
QFrame#panelFrame {
    border-radius: 16px;
    background-color: rgba(255, 255, 255, 218);
    border: 1px solid rgba(255, 255, 255, 160);
}
QLabel#label {
    color: white;
    font: 800 24pt "Microsoft JhengHei UI";
}
QLabel#subtitleLabel {
    color: rgba(255, 255, 255, 218);
    font: 11pt "Microsoft JhengHei UI";
}
QLabel#sectionLabel {
    color: rgb(47, 50, 80);
    font: 700 11pt "Microsoft JhengHei UI";
}
QListWidget#listWidget {
    border: 1px solid rgba(58, 62, 96, 45);
    border-radius: 12px;
    background: rgba(255, 255, 255, 230);
    padding: 8px;
    font: 10pt "Microsoft JhengHei UI";
    color: rgb(38, 40, 58);
}
QListWidget#previewListWidget {
    border: 0;
    border-radius: 12px;
    background: rgba(255, 255, 255, 120);
    padding: 8px;
}
QListWidget::item {
    border-radius: 8px;
    padding: 6px;
}
QListWidget::item:selected {
    background: rgba(105, 214, 224, 95);
    color: rgb(23, 32, 47);
}
QPushButton {
    border: 0;
    border-radius: 12px;
    min-height: 38px;
    padding: 8px 14px;
    font: 700 10pt "Microsoft JhengHei UI";
    color: rgb(22, 30, 48);
    background-color: rgb(170, 255, 255);
}
QPushButton:hover {
    background-color: rgb(196, 255, 247);
}
QPushButton:pressed {
    background-color: rgb(126, 225, 229);
    padding-top: 10px;
}
QPushButton#pushButton_3 {
    color: white;
    background-color: rgb(43, 47, 74);
}
QPushButton#pushButton_3:hover {
    background-color: rgb(63, 70, 108);
}
QPushButton#pushButton_4 {
    background-color: rgba(255, 255, 255, 210);
}
QComboBox {
    border: 0;
    border-radius: 12px;
    min-height: 38px;
    padding: 0 12px;
    font: 700 10pt "Microsoft JhengHei UI";
    color: rgb(22, 30, 48);
    background-color: rgba(255, 255, 255, 225);
}
QComboBox::drop-down {
    border: 0;
    width: 28px;
}
QProgressBar {
    min-height: 18px;
    border: 0;
    border-radius: 9px;
    background: rgba(255, 255, 255, 170);
    color: rgb(41, 44, 68);
    text-align: center;
    font: 9pt "Consolas";
}
QProgressBar::chunk {
    border-radius: 9px;
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0.5, x2:1, y2:0.5,
        stop:0 rgba(84, 226, 226, 255),
        stop:1 rgba(255, 110, 185, 255)
    );
}
""")

        self.rootLayout = QtWidgets.QVBoxLayout(layout_parent)
        self.rootLayout.setContentsMargins(28, 24, 28, 24)
        self.rootLayout.setSpacing(16)
        self.rootLayout.setObjectName("rootLayout")

        self.heroFrame = QtWidgets.QFrame(layout_parent)
        self.heroFrame.setObjectName("heroFrame")
        self.heroFrameLayout = QtWidgets.QVBoxLayout(self.heroFrame)
        self.heroFrameLayout.setContentsMargins(22, 18, 22, 18)
        self.heroFrameLayout.setSpacing(6)

        self.label = QtWidgets.QLabel(self.heroFrame)
        self.label.setObjectName("label")
        self.heroFrameLayout.addWidget(self.label)

        self.subtitleLabel = QtWidgets.QLabel(self.heroFrame)
        self.subtitleLabel.setObjectName("subtitleLabel")
        self.subtitleLabel.setWordWrap(True)
        self.heroFrameLayout.addWidget(self.subtitleLabel)
        self.rootLayout.addWidget(self.heroFrame)

        self.panelFrame = QtWidgets.QFrame(layout_parent)
        self.panelFrame.setObjectName("panelFrame")
        self.panelLayout = QtWidgets.QGridLayout(self.panelFrame)
        self.panelLayout.setContentsMargins(18, 16, 18, 16)
        self.panelLayout.setHorizontalSpacing(16)
        self.panelLayout.setVerticalSpacing(12)

        self.folderLabel = QtWidgets.QLabel(self.panelFrame)
        self.folderLabel.setObjectName("sectionLabel")
        self.panelLayout.addWidget(self.folderLabel, 0, 0)

        self.previewLabel = QtWidgets.QLabel(self.panelFrame)
        self.previewLabel.setObjectName("sectionLabel")
        self.panelLayout.addWidget(self.previewLabel, 0, 1)

        self.listWidget = QtWidgets.QListWidget(self.panelFrame)
        self.listWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listWidget.setMovement(QtWidgets.QListView.Static)
        self.listWidget.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget.setWordWrap(False)
        self.listWidget.setObjectName("listWidget")
        self.panelLayout.addWidget(self.listWidget, 1, 0)

        self.previewListWidget = QtWidgets.QListWidget(self.panelFrame)
        self.previewListWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.previewListWidget.setViewMode(QtWidgets.QListView.IconMode)
        self.previewListWidget.setMovement(QtWidgets.QListView.Static)
        self.previewListWidget.setResizeMode(QtWidgets.QListView.Adjust)
        self.previewListWidget.setIconSize(QtCore.QSize(92, 92))
        self.previewListWidget.setGridSize(QtCore.QSize(112, 126))
        self.previewListWidget.setSpacing(8)
        self.previewListWidget.setObjectName("previewListWidget")
        self.panelLayout.addWidget(self.previewListWidget, 1, 1)
        self.panelLayout.setColumnStretch(0, 2)
        self.panelLayout.setColumnStretch(1, 3)
        self.rootLayout.addWidget(self.panelFrame, 1)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setSpacing(10)
        self.buttonLayout.setObjectName("buttonLayout")

        self.comboBox = QtWidgets.QComboBox(layout_parent)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setMinimumHeight(38)
        self.buttonLayout.addWidget(self.comboBox)

        self.pushButton = GlowButton(layout_parent)
        self.pushButton.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.pushButton.setObjectName("pushButton")
        self.buttonLayout.addWidget(self.pushButton)

        self.pushButton_2 = GlowButton(layout_parent)
        self.pushButton_2.setObjectName("pushButton_2")
        self.buttonLayout.addWidget(self.pushButton_2)

        self.pushButton_4 = GlowButton(layout_parent)
        self.pushButton_4.setObjectName("pushButton_4")
        self.buttonLayout.addWidget(self.pushButton_4)

        self.pushButton_3 = GlowButton(layout_parent)
        self.pushButton_3.setEnabled(True)
        self.pushButton_3.setCheckable(False)
        self.pushButton_3.setDefault(False)
        self.pushButton_3.setFlat(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.buttonLayout.addWidget(self.pushButton_3)
        self.rootLayout.addLayout(self.buttonLayout)

        self.progressBar = QtWidgets.QProgressBar(layout_parent)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.rootLayout.addWidget(self.progressBar)

        self._add_shadow(self.heroFrame, 24, 0.22)
        self._add_shadow(self.panelFrame, 30, 0.18)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def _add_shadow(self, widget, blur_radius, opacity):
        shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur_radius)
        shadow.setOffset(0, 10)
        shadow.setColor(QtGui.QColor(24, 28, 48, int(255 * opacity)))
        widget.setGraphicsEffect(shadow)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "相似系列圖片自動整理系統 1.4"))
        self.label.setText(_translate("Form", "相似系列圖片自動整理系統"))
        self.subtitleLabel.setText(_translate("Form", "選擇或拖入圖片/資料夾，掃描後依照相似內容自動分組。"))
        self.folderLabel.setText(_translate("Form", "已加入的圖片或資料夾"))
        self.previewLabel.setText(_translate("Form", "圖片預覽"))
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
        self.comboBox.clear()
        self.comboBox.addItem(_translate("Form", "標準模式"), "standard")
        self.comboBox.addItem(_translate("Form", "嚴格模式"), "strict")
        self.comboBox.addItem(_translate("Form", "寬鬆模式"), "loose")
        self.comboBox.addItem(_translate("Form", "快速模式"), "fast")


import image_rc


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
