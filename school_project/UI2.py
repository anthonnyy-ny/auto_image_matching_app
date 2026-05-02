# -*- coding: utf-8 -*-

from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import class_list
from animated_ui import AnimatedBackgroundWidget, GlowButton

if not hasattr(class_list, "CF_list"):
    class_list.create_global()

ICON_DIR = Path(__file__).resolve().parent / "ui_view" / "png_icons"


class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1180, 760)
        mainWindow.setMinimumSize(QtCore.QSize(920, 620))
        mainWindow.setWindowIcon(self._icon(":/background image/pictureresult.ico"))
        mainWindow.setStyleSheet(self._style_sheet())

        self.centralwidget = AnimatedBackgroundWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.start_ai_motion()
        self.rootLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.rootLayout.setContentsMargins(22, 18, 22, 18)
        self.rootLayout.setSpacing(14)

        self.headerFrame = QtWidgets.QFrame(self.centralwidget)
        self.headerFrame.setObjectName("headerFrame")
        self.headerLayout = QtWidgets.QHBoxLayout(self.headerFrame)
        self.headerLayout.setContentsMargins(22, 16, 22, 16)
        self.headerLayout.setSpacing(16)

        self.titleBlock = QtWidgets.QVBoxLayout()
        self.titleBlock.setSpacing(3)
        self.titleLabel = QtWidgets.QLabel(self.headerFrame)
        self.titleLabel.setObjectName("titleLabel")
        self.subtitleLabel = QtWidgets.QLabel(self.headerFrame)
        self.subtitleLabel.setObjectName("subtitleLabel")
        self.titleBlock.addWidget(self.titleLabel)
        self.titleBlock.addWidget(self.subtitleLabel)
        self.headerLayout.addLayout(self.titleBlock, 1)

        self.lineEdit = QtWidgets.QLineEdit(self.headerFrame)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setMinimumWidth(260)
        self.lineEdit.setClearButtonEnabled(True)
        self.headerLayout.addWidget(self.lineEdit)
        self.rootLayout.addWidget(self.headerFrame)

        self.contentFrame = QtWidgets.QFrame(self.centralwidget)
        self.contentFrame.setObjectName("contentFrame")
        self.contentLayout = QtWidgets.QVBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(16, 16, 16, 16)
        self.contentLayout.setSpacing(12)

        self.tabWidget_2 = QtWidgets.QTabWidget(self.contentFrame)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tableLayout = QtWidgets.QVBoxLayout(self.tab_3)
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableLayout.setSpacing(0)

        self.tableWidget = QtWidgets.QTableWidget(self.tab_3)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(15)
        self.tableWidget.setRowCount(50)
        self.tableWidget.setIconSize(QtCore.QSize(150, 150))
        self.tableWidget.setAlternatingRowColors(False)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(160)
        self.tableWidget.verticalHeader().setDefaultSectionSize(160)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(120)
        self.tableWidget.verticalHeader().setMinimumSectionSize(120)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        for row in range(50):
            self.tableWidget.setVerticalHeaderItem(row, QtWidgets.QTableWidgetItem(str(row + 1)))
        for col in range(15):
            self.tableWidget.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(str(col + 1)))
        self.tableLayout.addWidget(self.tableWidget)

        self.tabWidget_2.addTab(self.tab_3, self._icon(":/background image/text-pageresult.ico"), "")
        self.tab_4 = QtWidgets.QWidget()
        self.tabWidget_2.addTab(self.tab_4, self._icon(":/background image/pictureresult.ico"), "")
        self.tab = QtWidgets.QWidget()
        self.tabWidget_2.addTab(self.tab, self._icon(":/background image/folderresult.ico"), "")
        self.tab_2 = QtWidgets.QWidget()
        self.tabWidget_2.addTab(self.tab_2, self._icon(":/background image/searchresult.ico"), "")
        self.contentLayout.addWidget(self.tabWidget_2)
        self.rootLayout.addWidget(self.contentFrame, 1)
        mainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setObjectName("menubar")
        mainWindow.setMenuBar(self.menubar)
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_3 = QtWidgets.QMenu(self.menubar)
        self.menu_4 = QtWidgets.QMenu(self.menubar)
        self.menu_5 = QtWidgets.QMenu(self.menubar)
        self.menu_C = QtWidgets.QMenu(self.menubar)
        self.menu_7 = QtWidgets.QMenu(self.menubar)
        self.menu_8 = QtWidgets.QMenu(self.menubar)
        self.menu_9 = QtWidgets.QMenu(self.menu_C)
        self.menu_6 = QtWidgets.QMenu(self.menu)

        self.statusBar = QtWidgets.QStatusBar(mainWindow)
        self.statusBar.setObjectName("statusBar")
        mainWindow.setStatusBar(self.statusBar)

        self.toolBar = QtWidgets.QToolBar(mainWindow)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setIconSize(QtCore.QSize(24, 24))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolBar.setMovable(False)
        mainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.dockWidget = QtWidgets.QDockWidget(mainWindow)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.sideLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.sideLayout.setContentsMargins(14, 14, 14, 14)
        self.sideLayout.setSpacing(10)
        self.sideTitle = QtWidgets.QLabel(self.dockWidgetContents)
        self.sideTitle.setObjectName("sideTitle")
        self.sideLayout.addWidget(self.sideTitle)

        self.pushButton = self._side_button(self.dockWidgetContents, "pushButton")
        self.pushButton_2 = self._side_button(self.dockWidgetContents, "pushButton_2")
        self.pushButton_3 = self._side_button(self.dockWidgetContents, "pushButton_3")
        self.pushButton_4 = self._side_button(self.dockWidgetContents, "pushButton_4")
        self.sideLayout.addWidget(self.pushButton)
        self.sideLayout.addWidget(self.pushButton_2)
        self.sideLayout.addWidget(self.pushButton_3)
        self.sideLayout.addWidget(self.pushButton_4)
        self.sideLayout.addSpacing(8)

        self.pushButton_5 = self._side_button(self.dockWidgetContents, "pushButton_5")
        self.pushButton_6 = self._side_button(self.dockWidgetContents, "pushButton_6")
        self.pushButton_7 = self._side_button(self.dockWidgetContents, "pushButton_7")
        self.pushButton_8 = self._side_button(self.dockWidgetContents, "pushButton_8")
        self.sideLayout.addWidget(self.pushButton_5)
        self.sideLayout.addWidget(self.pushButton_6)
        self.sideLayout.addWidget(self.pushButton_7)
        self.sideLayout.addWidget(self.pushButton_8)
        self.sideLayout.addSpacing(8)

        self.pushButton_9 = self._side_button(self.dockWidgetContents, "pushButton_9")
        self.pushButton_10 = self._side_button(self.dockWidgetContents, "pushButton_10")
        self.pushButton_11 = self._side_button(self.dockWidgetContents, "pushButton_11")
        self.pushButton_12 = self._side_button(self.dockWidgetContents, "pushButton_12")
        self.sideLayout.addWidget(self.pushButton_9)
        self.sideLayout.addWidget(self.pushButton_10)
        self.sideLayout.addWidget(self.pushButton_11)
        self.sideLayout.addWidget(self.pushButton_12)
        self.sideLayout.addStretch(1)
        self.dockWidget.setWidget(self.dockWidgetContents)
        mainWindow.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget)

        self._create_actions(mainWindow)
        self._wire_menus()
        self.retranslateUi(mainWindow)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def _icon(self, path):
        icon_name = path.rsplit("/", 1)[-1].replace(".ico", ".png")
        png_path = ICON_DIR / icon_name
        if png_path.exists():
            return QtGui.QIcon(str(png_path))
        return QtGui.QIcon(path)

    def _side_button(self, parent, name):
        button = GlowButton(parent)
        button.setObjectName(name)
        button.setMinimumHeight(36)
        return button

    def _add_shadow(self, widget, blur_radius, opacity):
        return

    def _start_intro_animation(self):
        return

    def _create_actions(self, mainWindow):
        self.action_F1 = QtGui.QAction(mainWindow)
        self.action_about = QtGui.QAction(mainWindow)
        self.action_4 = QtGui.QAction(self._icon(":/background image/exitresult.ico"), "", mainWindow)
        self.actionundo_CTRL_Z = QtGui.QAction(self._icon(":/background image/undoresult.ico"), "", mainWindow)
        self.actionRedo_Ctrl_Y = QtGui.QAction(self._icon(":/background image/redoresult.ico"), "", mainWindow)
        self.actionCut = QtGui.QAction(self._icon(":/background image/cutresult.ico"), "", mainWindow)
        self.actionCopy = QtGui.QAction(self._icon(":/background image/copyresult.ico"), "", mainWindow)
        self.actionPaste = QtGui.QAction(self._icon(":/background image/pasteresult.ico"), "", mainWindow)
        self.actionSelect_All_Ctrl_A = QtGui.QAction(mainWindow)
        self.action = QtGui.QAction(self._icon(":/background image/minimizeresult.ico"), "", mainWindow)
        self.action_3 = QtGui.QAction(mainWindow)
        self.action_7 = QtGui.QAction(mainWindow)
        self.action_8 = QtGui.QAction(self._icon(":/background image/gearresult.ico"), "", mainWindow)
        self.action_10 = QtGui.QAction(self._icon(":/background image/folderresult.ico"), "", mainWindow)
        self.action_11 = QtGui.QAction(self._icon(":/background image/disketteresult.ico"), "", mainWindow)
        self.action_12 = QtGui.QAction(mainWindow)
        self.action_13 = QtGui.QAction(mainWindow)
        self.action_19 = QtGui.QAction(mainWindow)
        self.action_2 = QtGui.QAction(mainWindow)
        self.action_5 = QtGui.QAction(self._icon(":/background image/add-fileresult.ico"), "", mainWindow)
        self.action_6 = QtGui.QAction(self._icon(":/background image/playresult.ico"), "", mainWindow)
        self.action_9 = QtGui.QAction(self._icon(":/background image/searchresult.ico"), "", mainWindow)
        self.action_14 = QtGui.QAction(mainWindow)
        self.action_15 = QtGui.QAction(self._icon(":/background image/full-screenresult.ico"), "", mainWindow)
        self.action_17 = QtGui.QAction(mainWindow)
        self.action_17.setCheckable(True)

    def _wire_menus(self):
        self.menu.addAction(self.action_5)
        self.menu.addAction(self.action_10)
        self.menu.addSeparator()
        self.menu.addAction(self.action_11)
        self.menu.addAction(self.action_12)
        self.menu.addAction(self.action_13)
        self.menu.addSeparator()
        self.menu.addAction(self.action_19)
        self.menu.addSeparator()
        self.menu.addAction(self.action_4)
        self.menu_2.addAction(self.action_F1)
        self.menu_2.addAction(self.action_7)
        self.menu_2.addSeparator()
        self.menu_2.addAction(self.action_3)
        self.menu_2.addAction(self.action_about)
        self.menu_3.addAction(self.actionundo_CTRL_Z)
        self.menu_3.addAction(self.actionRedo_Ctrl_Y)
        self.menu_3.addSeparator()
        self.menu_3.addAction(self.actionCut)
        self.menu_3.addAction(self.actionCopy)
        self.menu_3.addAction(self.actionPaste)
        self.menu_3.addAction(self.actionSelect_All_Ctrl_A)
        self.menu_4.addAction(self.action_8)
        self.menu_5.addAction(self.action)
        self.menu_9.addAction(self.action_17)
        self.menu_C.addAction(self.action_15)
        self.menu_C.addAction(self.menu_9.menuAction())
        self.menu_7.addAction(self.action_6)
        self.menu_8.addAction(self.action_9)
        self.menu_8.addAction(self.action_14)
        for menu in (self.menu, self.menu_3, self.menu_7, self.menu_8, self.menu_C, self.menu_4, self.menu_5, self.menu_2):
            self.menubar.addAction(menu.menuAction())
        for action in (self.action_5, self.action_10, self.action_11, self.action_6, self.action_9, self.action_8, self.action_15, self.action, self.action_4):
            self.toolBar.addAction(action)
            if action in (self.action_11, self.action_9, self.action_8, self.action):
                self.toolBar.addSeparator()

    def _style_sheet(self):
        return """
QWidget#centralwidget {
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgb(48, 31, 70),
        stop:0.30 rgb(126, 70, 150),
        stop:0.62 rgb(210, 118, 176),
        stop:0.84 rgb(242, 188, 220),
        stop:1 rgb(255, 247, 252)
    );
}
QFrame#headerFrame {
    border-radius: 18px;
    background-color: rgba(154, 76, 142, 138);
    border: 1px solid rgba(255, 232, 248, 168);
}
QFrame#contentFrame {
    border-radius: 18px;
    background-color: rgba(255, 238, 249, 112);
    border: 1px solid rgba(255, 255, 255, 150);
}
QLabel#titleLabel {
    color: white;
    font: 800 23pt "Microsoft JhengHei UI";
}
QLabel#subtitleLabel {
    color: rgba(255, 248, 253, 226);
    font: 10pt "Microsoft JhengHei UI";
}
QLineEdit#lineEdit {
    min-height: 38px;
    border: 1px solid rgba(255, 210, 236, 190);
    border-radius: 12px;
    background: rgba(255, 251, 254, 235);
    padding: 0 12px;
    color: rgb(35, 38, 58);
    font: 10pt "Microsoft JhengHei UI";
}
QTabWidget::pane {
    border: 0;
    background: transparent;
}
QTabBar::tab {
    min-width: 110px;
    min-height: 34px;
    margin-right: 8px;
    border-radius: 10px;
    color: rgba(255, 255, 255, 226);
    background: rgba(95, 54, 118, 118);
    font: 700 10pt "Microsoft JhengHei UI";
}
QTabBar::tab:selected {
    color: rgb(58, 39, 70);
    background: rgba(255, 250, 253, 238);
}
QTableWidget#tableWidget {
    border: 1px solid rgba(255, 222, 242, 150);
    border-radius: 14px;
    background: rgba(255, 249, 253, 232);
    gridline-color: rgba(255, 255, 255, 0);
    color: rgb(32, 35, 54);
    font: 10pt "Microsoft JhengHei UI";
    selection-background-color: rgba(255, 118, 190, 112);
    selection-color: rgb(25, 29, 45);
}
QTableWidget#tableWidget::item {
    border-radius: 12px;
    padding: 8px;
}
QHeaderView::section {
    border: 0;
    border-radius: 8px;
    padding: 6px;
    margin: 2px;
    color: rgb(65, 43, 80);
    background: rgba(255, 241, 249, 218);
    font: 700 9pt "Microsoft JhengHei UI";
}
QDockWidget {
    color: white;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    font: 700 10pt "Microsoft JhengHei UI";
}
QWidget#dockWidgetContents {
    background-color: rgba(46, 31, 70, 236);
}
QLabel#sideTitle {
    color: white;
    font: 800 13pt "Microsoft JhengHei UI";
}
QPushButton {
    min-height: 34px;
    border: 0;
    border-radius: 11px;
    padding: 7px 10px;
    color: rgb(26, 31, 48);
    background-color: rgb(176, 255, 252);
    font: 700 10pt "Microsoft JhengHei UI";
}
QPushButton:hover {
    background-color: rgb(255, 225, 245);
}
QPushButton:pressed {
    background-color: rgb(126, 225, 229);
    padding-top: 9px;
}
QMenuBar {
    color: rgb(245, 247, 255);
    background-color: rgb(46, 31, 70);
    font: 10pt "Microsoft JhengHei UI";
}
QMenuBar::item:selected {
    background: rgba(255, 255, 255, 40);
}
QMenu {
    color: rgb(32, 35, 54);
    background: rgba(255, 255, 255, 245);
    border: 1px solid rgba(40, 43, 70, 40);
    padding: 6px;
}
QMenu::item {
    padding: 7px 28px 7px 22px;
    border-radius: 7px;
}
QMenu::item:selected {
    background: rgba(255, 142, 202, 96);
}
QToolBar {
    background: rgb(46, 31, 70);
    border: 0;
    spacing: 8px;
    padding: 6px;
}
QToolButton {
    border: 0;
    border-radius: 9px;
    padding: 6px;
    background: rgba(255, 255, 255, 38);
}
QToolButton:hover {
    background: rgba(255, 174, 220, 102);
}
QStatusBar {
    color: rgb(245, 247, 255);
    background: rgb(46, 31, 70);
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
    border: 0;
    margin: 2px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: rgba(172, 111, 188, 160);
    border-radius: 6px;
    min-height: 28px;
    min-width: 28px;
}
"""

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "相似系列圖片自動整理系統 1.4"))
        self.titleLabel.setText(_translate("mainWindow", "分組結果工作台"))
        self.subtitleLabel.setText(_translate("mainWindow", "瀏覽、調整與保存相似圖片分組"))
        self.lineEdit.setPlaceholderText(_translate("mainWindow", "搜尋檔名或分組..."))
        self.sideTitle.setText(_translate("mainWindow", "整理工具"))
        self.tableWidget.setStatusTip(_translate("mainWindow", "雙擊圖片可以查看或編輯"))
        self.tabWidget_2.setTabText(0, _translate("mainWindow", "分組結果"))
        self.tabWidget_2.setTabText(1, _translate("mainWindow", "檢視"))
        self.tabWidget_2.setTabText(2, _translate("mainWindow", "資料夾"))
        self.tabWidget_2.setTabText(3, _translate("mainWindow", "搜尋"))
        self.menu.setTitle(_translate("mainWindow", "文件"))
        self.menu_2.setTitle(_translate("mainWindow", "說明"))
        self.menu_3.setTitle(_translate("mainWindow", "編輯"))
        self.menu_4.setTitle(_translate("mainWindow", "設定"))
        self.menu_5.setTitle(_translate("mainWindow", "窗口"))
        self.menu_C.setTitle(_translate("mainWindow", "查看"))
        self.menu_9.setTitle(_translate("mainWindow", "工具欄"))
        self.menu_7.setTitle(_translate("mainWindow", "執行"))
        self.menu_8.setTitle(_translate("mainWindow", "搜索"))
        self.toolBar.setWindowTitle(_translate("mainWindow", "工具列"))
        labels = {
            self.pushButton: ("增加列", "Q"),
            self.pushButton_2: ("減少列", "W"),
            self.pushButton_3: ("隱藏單元格", "A"),
            self.pushButton_4: ("顯示單元格", "S"),
            self.pushButton_5: ("增加行", "E"),
            self.pushButton_6: ("減少行", "R"),
            self.pushButton_7: ("縮小單元格", "D"),
            self.pushButton_8: ("放大單元格", "F"),
            self.pushButton_9: ("隱藏垂直標頭", "Z"),
            self.pushButton_10: ("顯示垂直標頭", "X"),
            self.pushButton_11: ("隱藏水平標頭", "C"),
            self.pushButton_12: ("顯示水平標頭", "V"),
        }
        for button, (text, shortcut) in labels.items():
            button.setText(_translate("mainWindow", text))
            button.setToolTip(_translate("mainWindow", text + " (" + shortcut + ")"))
            button.setShortcut(_translate("mainWindow", shortcut))
        action_labels = [
            (self.action_F1, "使用說明", "F1"),
            (self.action_about, "關於", ""),
            (self.action_4, "退出", "Ctrl+Q"),
            (self.actionundo_CTRL_Z, "撤消", "Ctrl+Z"),
            (self.actionRedo_Ctrl_Y, "重做", "Ctrl+Y"),
            (self.actionCut, "剪切", "Ctrl+X"),
            (self.actionCopy, "複製", "Ctrl+C"),
            (self.actionPaste, "貼上", "Ctrl+V"),
            (self.actionSelect_All_Ctrl_A, "全選", "Ctrl+A"),
            (self.action, "最小化", "Esc"),
            (self.action_3, "檢查更新", ""),
            (self.action_7, "隱私聲明", ""),
            (self.action_8, "偏好設定", ""),
            (self.action_10, "打開", "Ctrl+O"),
            (self.action_11, "保存", "Ctrl+S"),
            (self.action_12, "另存為", ""),
            (self.action_13, "全部保存", "Ctrl+Shift+S"),
            (self.action_19, "打印", "Ctrl+P"),
            (self.action_2, "清除菜單", ""),
            (self.action_5, "新建", "Ctrl+N"),
            (self.action_6, "執行", "F5"),
            (self.action_9, "搜索文字", "Ctrl+F"),
            (self.action_14, "搜索資料夾", "Ctrl+Shift+F"),
            (self.action_15, "全屏幕模式", "F11"),
            (self.action_17, "資料夾", ""),
        ]
        for action, text, shortcut in action_labels:
            action.setText(_translate("mainWindow", text))
            action.setStatusTip(_translate("mainWindow", text))
            if shortcut:
                action.setShortcut(_translate("mainWindow", shortcut))
        self.action_10.setIconText(_translate("mainWindow", "打開資料夾"))




if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_mainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec())
