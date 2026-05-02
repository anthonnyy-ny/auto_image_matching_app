# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 16:20:56 2022

@author: User
"""

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFileDialog
import cv2
import csv
import json
import time
import sys

#from concurrent.futures import thread
#from ctypes import BigEndianStructure
import os
#from random import shuffle
#from tokenize import group
#from turtle import down, up
import cv2
import numpy as np
#import pandas as pd
#from matplotlib import pyplot as plt
import math
from math import *
from datetime import datetime


from PyQt6 import QtPrintSupport, QtGui
from PyQt6.QtCore import Qt, QMimeData, QDate, QDateTime, QTime, QStringListModel, QSize
from PyQt6.QtGui import QAction, QIcon, QPainter, QBrush, QPixmap, QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtPrintSupport import QPageSetupDialog, QPrinter, QPrintDialog
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QFormLayout, QLabel, QLineEdit, QPushButton, QGridLayout, \
    QCalendarWidget, QVBoxLayout, QDateTimeEdit, QMainWindow, QTextEdit, QStatusBar, QFileDialog, QDialog, \
    QTableView, QMessageBox, QListView, QListWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView
    
from UI2 import Ui_mainWindow
from savefile import Ui_Dialog
from result_model import ResultTableModel, ThumbnailDelegate, ThumbnailManager

import class_list
from app_paths import debug_output_dir, default_open_dir, downloads_dir
from image_utils import iter_image_files, jpg_filename


class SaveGroupsWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(int, int, str)
    finished = QtCore.pyqtSignal(str, int, int, list)
    failed = QtCore.pyqtSignal(str)

    def __init__(self, groups_snapshot, output_root, parent=None):
        super().__init__(parent)
        self.groups_snapshot = groups_snapshot
        self.output_root = output_root

    def run(self):
        try:
            os.makedirs(self.output_root, exist_ok=True)
            total = sum(len(group["images"]) for group in self.groups_snapshot)
            done = 0
            saved = 0
            errors = []
            base_mtime = time.time()
            manifest_rows = []

            for group_index, group in enumerate(self.groups_snapshot, start=1):
                group_name = group["name"]
                group_dir = os.path.join(self.output_root, group_name)
                os.makedirs(group_dir, exist_ok=True)

                for image in group["images"]:
                    try:
                        store_img = read_cv_image(image["source_path"])
                        if store_img is None:
                            raise ValueError("Image could not be read")
                        output_path = os.path.join(group_dir, transfer_filename(image["filename"]))
                        if not cv2.imwrite(output_path, store_img):
                            raise ValueError("Image could not be written")
                        manifest_rows.append({
                            "group": group_name,
                            "filename": image["filename"],
                            "source_path": image["source_path"],
                            "saved_path": output_path,
                        })
                        saved += 1
                    except Exception as exc:
                        errors.append(group_name + " / " + image["filename"] + ": " + str(exc))
                    finally:
                        done += 1
                        self.progress.emit(done, total, group_name)

                group_mtime = base_mtime - group_index
                os.utime(group_dir, (group_mtime, group_mtime))

            manifest_csv = os.path.join(self.output_root, "manifest.csv")
            with open(manifest_csv, "w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["group", "filename", "source_path", "saved_path"])
                writer.writeheader()
                writer.writerows(manifest_rows)
            manifest_json = os.path.join(self.output_root, "manifest.json")
            with open(manifest_json, "w", encoding="utf-8") as json_file:
                json.dump(manifest_rows, json_file, ensure_ascii=False, indent=2)

            self.finished.emit(self.output_root, saved, total, errors)
        except Exception as exc:
            self.failed.emit(str(exc))




def new_resize_img(img, new_scale):                 #check
    height, width = img.shape[:2]
    scale = new_scale

    img = cv2.resize(img, (int(scale*width), int(scale*height)),
                     interpolation=cv2.INTER_AREA)

    return img


def a_hash(img):                                    #check

    # 轉 8*8
    img = cv2.resize(img, (8, 8), interpolation=cv2.INTER_CUBIC)
    # 轉 灰階圖
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 8*8灰階值總和
    sum_gray = 0
    # hash 字串
    hash_str = ''

    # 求灰階值總和
    for i in range(8):
        for j in range(8):
            sum_gray += int(gray[i][j])

    # 8*8灰階圖 平均
    average_gray = sum_gray/64

    # 比較
    for i in range(8):
        for j in range(8):
            if(gray[i][j] > average_gray):
                hash_str += '1'
            else:
                hash_str += '0'

    return hash_str


def cam_hash(hash_1, hash_2):                       #check

    # 記 hash_1 , hash_2  一樣 次數
    not_same = 0

    # 比對 hash_1 , hash_2 相同的次數
    for i in range(64):
        if(hash_1[i] != hash_2[i]):
            not_same += 1

    return (not_same)

def showIMG(name, img):                             #check
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test_angle(tar_Point, tem_Point, select_point): #check

    va_x = tar_Point[select_point[0]][0]-tar_Point[select_point[1]][0]
    va_y = tar_Point[select_point[0]][1]-tar_Point[select_point[1]][1]
    vb_x = tar_Point[select_point[2]][0]-tar_Point[select_point[1]][0]
    vb_y = tar_Point[select_point[2]][1]-tar_Point[select_point[1]][1]

    vc_x = tem_Point[select_point[0]][0]-tem_Point[select_point[1]][0]
    vc_y = tem_Point[select_point[0]][1]-tem_Point[select_point[1]][1]
    vd_x = tem_Point[select_point[2]][0]-tem_Point[select_point[1]][0]
    vd_y = tem_Point[select_point[2]][1]-tem_Point[select_point[1]][1]

    long_A=sqrt((va_x**2+va_y**2)*(vb_x**2+vb_y**2))
    long_B=sqrt((vc_x**2+vc_y**2)*(vd_x**2+vd_y**2))

    if (long_A==0)|(long_B==0):
#        print("\nlong is 0 \n")
        return False

    cosA = (va_x*vb_x+va_y*vb_y) / long_A
    cosB = (vc_x*vd_x+vc_y*vd_y) / long_B


    A = math.degrees(np.arccos(cosA))
    B = math.degrees(np.arccos(cosB))

    if((A<=5) | (B<=5)):    return False

    if (abs(A-B) <= 5):         #double check
        va_x = tar_Point[select_point[1]][0]-tar_Point[select_point[0]][0]
        va_y = tar_Point[select_point[1]][1]-tar_Point[select_point[0]][1]
        vb_x = tar_Point[select_point[2]][0]-tar_Point[select_point[0]][0]
        vb_y = tar_Point[select_point[2]][1]-tar_Point[select_point[0]][1]

        vc_x = tem_Point[select_point[1]][0]-tem_Point[select_point[0]][0]
        vc_y = tem_Point[select_point[1]][1]-tem_Point[select_point[0]][1]
        vd_x = tem_Point[select_point[2]][0]-tem_Point[select_point[0]][0]
        vd_y = tem_Point[select_point[2]][1]-tem_Point[select_point[0]][1]

        long_A=sqrt((va_x**2+va_y**2)*(vb_x**2+vb_y**2))
        long_B=sqrt((vc_x**2+vc_y**2)*(vd_x**2+vd_y**2))

        A = math.degrees(np.arccos(cosA))
        B = math.degrees(np.arccos(cosB))
        if((A<=5) | (B<=5)):    return False
        if(abs(A-B) <= 5):     return True

#    print("\nFinal test angle False")
    return False

def test_rectangle(point_one,point_two,select_point):#check
    #min                                                #caculate init width hight ratio
    one_x = point_one[select_point[0]][0]
    one_y = point_one[select_point[0]][1]
    two_x = point_two[select_point[2]][0]
    two_y = point_two[select_point[2]][1]
    #max
    one_X = point_one[select_point[0]][0]
    one_Y = point_one[select_point[0]][1]
    two_X = point_two[select_point[2]][0]
    two_Y = point_two[select_point[2]][1]

    for i in select_point:
        if(point_one[i][0]<one_x):  one_x=point_one[i][0]       #min_x  point_one
        if(point_one[i][0]>one_X):  one_X=point_one[i][0]       #max_X
        if(point_one[i][1]<one_y):  one_y=point_one[i][1]       #min_y
        if(point_one[i][1]>one_Y):  one_Y=point_one[i][1]       #max_Y
        if(point_two[i][0]<two_x):  two_x=point_two[i][0]       #min_x  point two
        if(point_two[i][0]>two_X):  two_X=point_two[i][0]       #max_X
        if(point_two[i][1]<two_y):  two_y=point_two[i][1]       #min_y
        if(point_two[i][1]>two_Y):  two_Y=point_two[i][1]       #max_Y

    div_one_x=one_X-one_x
    div_one_y=one_Y-one_y

    if((div_one_x<=0)|(div_one_y<=0)):  return False
    one_rate=div_one_x/div_one_y

    div_two_x=two_X-two_x
    div_two_y=two_Y-two_y


    if((div_two_x==0)|(div_two_y<=0)):  return False
    two_rate=div_two_x/div_two_y

    #a:b==c:d
    miss_rate=0.1

    if((abs(1-(one_rate/two_rate))<miss_rate)): return True

    return False

def Find_LU(arr,select):
    Up=arr[select[0]][1]
    Left=arr[select[0]][0]
    Down=arr[select[0]][1]
    Right=arr[select[0]][0]
    for i in select:
        if( Up>arr[i][1]):     Up=arr[i][1]
        if( Left>arr[i][0]):   Left=arr[i][0]
        if( Down<arr[i][1]):   Down=arr[i][1]
        if( Right<arr[i][0]):  Right=arr[i][0]
    return Left,Up,Right,Down



def vector(tar,tem,point):          #check

    tarv_x=tar[point[1]][0]-tar[point[0]][0]
    tarv_y=tar[point[1]][1]-tar[point[0]][1]
    temv_x=tem[point[1]][0]-tem[point[0]][0]
    temv_y=tem[point[1]][1]-tem[point[0]][1]

    tar_square=tarv_x**2+tarv_y**2
    tem_square=temv_x**2+temv_y**2

    ratio=tar_square/tem_square

    return ratio

sift = cv2.SIFT_create()
bf = cv2.BFMatcher(crossCheck=True)


def read_cv_image(name):
    image = cv2.imread(name)
    if image is not None:
        return image

    qt_image = QImage(name)
    if qt_image.isNull() and QtWidgets.QApplication.instance() is not None:
        icon = QIcon(name)
        sizes = icon.availableSizes()
        if sizes:
            size = max(sizes, key=lambda value: value.width() * value.height())
            pixmap = icon.pixmap(size)
            qt_image = pixmap.toImage()
    if qt_image.isNull():
        return None
    qt_image = qt_image.convertToFormat(QImage.Format.Format_RGB888)
    width = qt_image.width()
    height = qt_image.height()
    bytes_per_line = qt_image.bytesPerLine()
    ptr = qt_image.bits()
    ptr.setsize(height * bytes_per_line)
    arr = np.frombuffer(ptr, np.uint8).reshape((height, bytes_per_line // 3, 3))
    arr = arr[:, :width, :]
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR).copy()

class IMG:
    def __init__(self,name,filename):
        self.name=name
        self.filename=filename
        self.img=read_cv_image(name)
        self.gray_img=[]
        self.kp=[]
        self.des=[]
        self.area=0
        self.width=0
        self.hight=0


    def img_shape(self):        #check

        if self.img is None:
            raise ValueError("Image could not be read: " + self.name)
        hight,width=self.img.shape[:2]
        if((width>=1000)&(hight>=1000)):
            self.img=new_resize_img(self.img,2**(-1))
        elif((width>=2000)&(hight>=2000)):
            self.img=new_resize_img(self.img,4**(-1))
        elif((width>=4000)&(hight>=4000)):
            self.img=new_resize_img(self.img,8**(-1))
        #cv2.imwrite("D:/source/vscode/python_project/check_img/img"+str(self.filename)+".jpg", self.img)
        self.gray_img=cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        self.hight,self.width=self.img.shape[:2]
        self.area=self.hight*self.width
        #cv2.imwrite("D:/source/vscode/python_project/check_img/gray"+str(self.filename)+".jpg", self.gray_img)

    def create_sift(self):      #check
        self.kp,self.des=sift.detectAndCompute(self.gray_img, None)

    def showIMG(self):          #check
        cv2.imshow(self.name, self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def showGrayIMG(self):      #check
        cv2.imshow(self.name, self.gray_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def showName(self):         #check
        print("IMG Name : ",self.name)

img=[]

class BUF_IMG:
    def __init__(self,img,width,hight,area,left,up,right,down):

        self.img=img
        self.width=width
        self.hight=hight
        self.area=area
        self.left=left
        self.up=up
        self.right=right
        self.down=down

    def resize_total(self,k):       #check

        self.area*=(k**(2))
        self.hight*=k
        self.width*=k
        self.left*=k
        self.up*=k
        self.right*=k
        self.down*=k
        self.img = cv2.resize(self.img, (int(self.width), int(self.hight)),
                     interpolation=cv2.INTER_AREA)

    def draw_circle(self,name):     #check
        img=self.img
        b_img=self.img
        cv2.circle(b_img,(int(self.y),int(self.x)),20,(0,0,255),-1)
        cv2.imwrite(str(debug_output_dir() / ("buf_" + name + ".jpg")), b_img)
        self.img=img

def read_directory(directory_name): #check

   for image_path in iter_image_files(directory_name):

        name_string = str(image_path)

        buf=IMG(name_string,image_path.name)
        buf.img_shape()
        buf.create_sift()
        img.append(buf)

#button_show=True

def drawKeyPoint(img_2, kp_2, img_1,kp_1, Three,save_img):
    print("len : ",len(Three))
        # Four
    img_out = cv2.drawMatches(img_2, kp_2, img_1,kp_1, Three[:], None, flags=2)
                                                    #畫特定kp    特徵點是否要畫
    showIMG("img_out", img_out)
    print("key point match len : ",len(Three))
    cv2.imwrite(str(debug_output_dir() / ("out_img_" + str(save_img) + ".jpg")), img_out)

def showCutIMG(img_1,img_2,save_img):
    print("save img : ",save_img,"\n")
    cv2.imwrite(str(debug_output_dir() / ("big_" + str(save_img) + ".jpg")), img_1)
    cv2.imwrite(str(debug_output_dir() / ("small_" + str(save_img) + ".jpg")), img_2)


def sift_ahash(img_1,img_2):
    save_img=0
    IMG_1=img_1
    IMG_2=img_2

    if IMG_1.des is None or IMG_2.des is None:
        return False, False

    match=bf.match(IMG_2.des,IMG_1.des)
    match = sorted(match, key=lambda x: x.distance)

    catch_match=5
    if len(match) < catch_match:
        return False, False

    IMG_1_Point = np.zeros((5,2))
    IMG_2_Point = np.zeros((5,2))

    point_index=0
    match_index=0
    match_list=[]
    while(point_index<catch_match):
        if match_index >= len(match):
            return False, False
        x, y = IMG_1.kp[match[match_index].trainIdx].pt
        a, b = IMG_2.kp[match[match_index].queryIdx].pt

        same=False
        for i in range(point_index):
            IMG_1_x_first, IMG_1_y_first = IMG_1.kp[match[i].trainIdx].pt
            IMG_2_x_first, IMG_2_y_first = IMG_2.kp[match[i].queryIdx].pt
            gap=50
            if((abs(x-IMG_1_x_first)<gap) & (abs(y-IMG_1_y_first)<gap))|( (abs(a-IMG_2_x_first)<gap) & (abs(b-IMG_2_y_first)<gap)):
                match_index += 1
                same=True
                break

        if(same):   continue

        IMG_1_Point[point_index][0] = x
        IMG_1_Point[point_index][1] = y
        IMG_2_Point[point_index][0] = a
        IMG_2_Point[point_index][1] = b

        match_list.append(match_index)
        match_index += 1
        point_index += 1


    Three = []
    for i in range(catch_match):
        Three.append(match[match_list[i]])

    #drawKeyPoint(IMG_2.img, IMG_2.kp, IMG_1.img,IMG_1.kp, Three,save_img)       #畫兩張關鍵點匹配位置

    Found = False
    count=0
    scale_index=0


    for flag_one in range(catch_match):
        for flag_two in range(flag_one+1, catch_match):

            count+=1
            select_point = [0, 1, 2, 3, 4]
            select_point.pop(4-flag_one)
            select_point.pop(4-flag_two)

        # < test angle >

            Not_Use_One = 4-flag_one
            Not_Use_Two = 4-flag_two
            Similar = test_rectangle(IMG_1_Point,IMG_2_Point, select_point)

            #print("similar")
            if not(Similar): continue

            Same_angle = test_angle(IMG_1_Point, IMG_2_Point, select_point)                                                # < 角度 >

            #print("angle")
            if not(Same_angle):            continue

        # < test LU ratio >

            Left,Up,Right,Down=Find_LU(IMG_1_Point,select_point)
            BUF_one=BUF_IMG(IMG_1.img,IMG_1.width,IMG_1.hight,IMG_1.area,Left,Up,Right,Down)
            Left,Up,Right,Down=Find_LU(IMG_2_Point,select_point)
            BUF_two=BUF_IMG(IMG_2.img,IMG_2.width,IMG_2.hight,IMG_2.area,Left,Up,Right,Down)

        # < test scale >

            long_ratio =  vector(IMG_1_Point,IMG_2_Point,select_point)

            #print("long_ratio : ",long_ratio)

            new_scale=(sqrt(long_ratio))

            #print("new_scale : ",new_scale)

            if(new_scale>=1):
                BUF_one.resize_total(new_scale**(-1))
            else:
                BUF_two.resize_total(new_scale)


            if(BUF_one.up>BUF_two.up):
                tem_up=BUF_two.up
            else:
                tem_up=BUF_one.up

            if((BUF_one.hight-BUF_one.down)>(BUF_two.hight-BUF_two.down)):
                tem_down=BUF_two.hight-BUF_two.down
            else:
                tem_down=BUF_one.hight-BUF_one.down

            if((BUF_one.left)>(BUF_two.left)):
                tem_left=BUF_two.left
            else:
                tem_left=BUF_one.left

            if((BUF_one.width-BUF_one.right)>(BUF_two.width-BUF_two.right)):
                tem_right=BUF_two.width-BUF_two.right
            else:
                tem_right=BUF_one.width-BUF_one.right

            tem_up=int(tem_up)
            tem_down=int(tem_down)
            tem_right=int(tem_right)
            tem_left=int(tem_left)


            b_l=int(BUF_one.left)
            b_u=int(BUF_one.up)
            b_r=int(BUF_one.right)
            b_d=int(BUF_one.down)

            h_1=b_u-tem_up
            w_1=b_l-tem_left
            h_2=b_d+tem_down
            w_2=b_r+tem_right

            if(h_1>h_2):         continue
            if((h_2-h_1)<50):    continue           #  <====  可調
            if(w_1>w_2):         continue
            if((w_2-w_1)<50):    continue           #  <====  可調

            IMG_one=BUF_one.img[h_1:h_2,w_1:w_2]

            b_l=int(BUF_two.left)
            b_u=int(BUF_two.up)
            b_r=int(BUF_two.right)
            b_d=int(BUF_two.down)

            h_1=b_u-tem_up
            w_1=b_l-tem_left
            h_2=b_d+tem_down
            w_2=b_r+tem_right

            if(h_1>h_2):         continue
            if((h_2-h_1)<50):    continue                       #  <====  可調
            if(w_1>w_2):         continue
            if((w_2-w_1)<50):    continue                       #  <====  可調

            IMG_two=BUF_two.img[h_1:h_2,w_1:w_2]


            #showCutIMG(IMG_one,IMG_2,save_img)

            dis=cam_hash(a_hash(IMG_one),a_hash(IMG_two))
            #print("dis : ",dis)
            if(dis<10):
                if(BUF_one.area>BUF_two.area):
                    return True, True
                else:
                    return True, False
            save_img+=1

    return False,False


class classification:
    def __init__(self,img):
        self.same=[img]
        self.img_count=1
    def save_img(self,index,big_small):         #check
        if(big_small):
            self.same.insert(0,index)
        else:
            self.same.append(index)
        self.img_count+=1

    def union(self,buf_classification):         #check
        buf=buf_classification.same.pop()
        self.same+=buf_classification.same
        self.same.insert(0,buf)
        self.img_count+=buf_classification.img_count



def PRINT_GROUP(buf_list):                      #check
    print("\n")
    for i in range(len(buf_list)):
        print("Group ",i," : ",end="")
        for buf in buf_list[i].same:
            print(buf.filename," ",end="")
        print("")
    print("\n")

def transfer_filename( buf_filename):
    return jpg_filename(buf_filename)
#============================================================================================


class ImagePreviewDialog(QtWidgets.QDialog):
    def __init__(self, image_path, filename, group_name, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle(filename)
        self.resize(860, 640)
        self.setMinimumSize(560, 420)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.title = QtWidgets.QLabel(filename)
        self.title.setStyleSheet('font: 700 14pt "Microsoft JhengHei UI";')
        layout.addWidget(self.title)

        self.meta = QtWidgets.QLabel(group_name + "    " + image_path)
        self.meta.setWordWrap(True)
        self.meta.setStyleSheet('color: rgb(80, 84, 110); font: 10pt "Microsoft JhengHei UI";')
        layout.addWidget(self.meta)

        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setStyleSheet("background: rgb(30, 32, 48); border-radius: 10px;")
        layout.addWidget(self.imageLabel, 1)

        buttons = QtWidgets.QHBoxLayout()
        open_button = QtWidgets.QPushButton("打开所在文件夹")
        close_button = QtWidgets.QPushButton("关闭")
        open_button.clicked.connect(self.open_folder)
        close_button.clicked.connect(self.accept)
        buttons.addStretch(1)
        buttons.addWidget(open_button)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)
        self.update_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            self.imageLabel.setText("无法预览图片")
            return
        target = self.imageLabel.size() - QtCore.QSize(24, 24)
        self.imageLabel.setPixmap(pixmap.scaled(target, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def open_folder(self):
        folder = os.path.dirname(self.image_path)
        if hasattr(os, "startfile"):
            os.startfile(folder)



class MainWindow_controller2(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        self.thumbnail_manager = ThumbnailManager(parent=self)
        self.result_model = ResultTableModel(class_list.CF_list, self)
        self.thumbnail_delegate = ThumbnailDelegate(self.thumbnail_manager, self.ui.tableWidget)
        self.ui.tableWidget.setModel(self.result_model)
        self.ui.tableWidget.setItemDelegate(self.thumbnail_delegate)
        self.thumbnail_manager.thumbnailReady.connect(self._thumbnail_ready)
        self.ui.tableWidget.verticalScrollBar().valueChanged.connect(self.prefetch_visible_thumbnails)
        self.ui.tableWidget.horizontalScrollBar().valueChanged.connect(self.prefetch_visible_thumbnails)
        self.save_worker = None
        self.save_progress = QtWidgets.QProgressBar(self)
        self.save_progress.setMaximumWidth(220)
        self.save_progress.setVisible(False)
        self.ui.statusBar.addPermanentWidget(self.save_progress)
        self.setup_control()
        self.IsStore=0
        
    def setup_control(self):
        
       self.ui.statusBar.showMessage("Ready", 5000)
       self.ui.action_11.triggered.connect(self.save_group)
       self.ui.action_11.setToolTip("保存（Ctrl+S)")
       self.ui.action_5.setToolTip("新建（Ctrl+N)")
       self.ui.action_10.setToolTip("打開資料夾（Ctrl+O)")
       self.ui.action_10.triggered.connect(self.openFile)
       self.ui.action_6.setToolTip("執行（F5)")
       self.ui.action_15.setToolTip("全屏幕模式（F11)")
       self.ui.action.setToolTip("最小化（F12)")
       self.ui.action_4.setToolTip("退出（Ctrl+Q)")
       self.ui.action_4.triggered.connect(self.close)
       self.ui.action_15.triggered.connect(self.showFullScreen)
       self.ui.action.triggered.connect(self.showMaximized)
       self.ui.toolBar.addWidget(self.ui.lineEdit)
       
       self.ui.pushButton.clicked.connect(self.addcolumn)
       self.ui.pushButton_2.clicked.connect(self.deletecolumn)
       self.ui.pushButton_3.clicked.connect(self.hidegrid)
       self.ui.pushButton_4.clicked.connect(self.showgrid)
       self.ui.pushButton_5.clicked.connect(self.addrow)
       self.ui.pushButton_6.clicked.connect(self.deleterow)
       self.ui.pushButton_7.clicked.connect(self.resizeRowColumn)
       self.ui.pushButton_8.clicked.connect(self.recoverRowColumn)
       self.ui.pushButton_9.clicked.connect(self.hideVerticalHeader)
       self.ui.pushButton_10.clicked.connect(self.showVerticalHeader)
       self.ui.pushButton_11.clicked.connect(self.hideHorizontallHeader)
       self.ui.pushButton_12.clicked.connect(self.showHorizontallHeader)
       self.ui.tableWidget.doubleClicked.connect(self.preview_item)
       self.ui.lineEdit.textChanged.connect(self.filter_results)

       self.populate_results()
       return

    def populate_results(self):
        groups = class_list.CF_list
        group_count = len(groups)
        self.thumbnail_manager.clear_memory()
        self.result_model.set_groups(groups)
        for column in range(self.result_model.columnCount()):
            self.ui.tableWidget.setColumnWidth(column, 165)
        for row in range(self.result_model.rowCount()):
            self.ui.tableWidget.setRowHeight(row, 165)
        self.ui.statusBar.showMessage("Loaded " + str(group_count) + " groups, lazy thumbnails enabled", 5000)
        self.animate_results()
        QtCore.QTimer.singleShot(0, self.prefetch_visible_thumbnails)

    def filter_results(self, text):
        self.result_model.set_filter_text(text)
        for column in range(self.result_model.columnCount()):
            self.ui.tableWidget.setColumnWidth(column, 165)
        for row in range(self.result_model.rowCount()):
            self.ui.tableWidget.setRowHeight(row, 165)
        shown = len(self.result_model.visible_rows)
        total = len(self.result_model.groups)
        if text.strip():
            self.ui.statusBar.showMessage("Showing " + str(shown) + " of " + str(total) + " groups", 2500)
        QtCore.QTimer.singleShot(0, self.prefetch_visible_thumbnails)

    def animate_results(self):
        self.ui.tableWidget.viewport().update()

    def _thumbnail_ready(self, source_path):
        self.ui.tableWidget.viewport().update()

    def prefetch_visible_thumbnails(self):
        view = self.ui.tableWidget
        model = self.result_model
        if model.rowCount() <= 0 or model.columnCount() <= 0:
            return
        viewport = view.viewport()
        top_left = view.indexAt(QtCore.QPoint(0, 0))
        bottom_right = view.indexAt(QtCore.QPoint(max(0, viewport.width() - 1), max(0, viewport.height() - 1)))
        first_row = top_left.row() if top_left.isValid() else 0
        first_col = top_left.column() if top_left.isValid() else 0
        last_row = bottom_right.row() if bottom_right.isValid() else min(model.rowCount() - 1, first_row + 5)
        last_col = bottom_right.column() if bottom_right.isValid() else min(model.columnCount() - 1, first_col + 6)
        first_row = max(0, first_row - 1)
        first_col = max(0, first_col - 1)
        last_row = min(model.rowCount() - 1, last_row + 2)
        last_col = min(model.columnCount() - 1, last_col + 2)
        for row in range(first_row, last_row + 1):
            for column in range(first_col, last_col + 1):
                image_path = model.index(row, column).data(ResultTableModel.ImagePathRole)
                if image_path:
                    self.thumbnail_manager.request(image_path)

    def preview_item(self, index):
        if not index.isValid():
            return
        image_path = index.data(ResultTableModel.ImagePathRole)
        group_name = index.data(ResultTableModel.GroupNameRole) or ""
        if not image_path:
            return
        dialog = ImagePreviewDialog(image_path, index.data() or "", group_name, self)
        dialog.exec()

    def addrow(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.result_model.insert_extra_row()
        self.ui.tableWidget.setRowHeight(self.result_model.rowCount() - 1, 165)
        self.IsStore+=1
    
    def deleterow(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.result_model.remove_extra_row()
        self.IsStore+=1
        
    
    def addcolumn(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.result_model.insert_extra_column()
        self.ui.tableWidget.setColumnWidth(self.result_model.columnCount() - 1, 165)
        self.IsStore+=1
    
    def deletecolumn(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.result_model.remove_extra_column()
        self.IsStore+=1

    def hidegrid(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.ui.tableWidget.setShowGrid(False)
        self.IsStore+=1
    
    def showgrid(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.ui.tableWidget.setShowGrid(True)
        self.IsStore+=1
    
    def resizeRowColumn(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()
        self.IsStore+=1
    
    def recoverRowColumn(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        row_i=col_j=0
        for row_i in range(self.result_model.rowCount()):
          for col_j in range(self.result_model.columnCount()):
              self.ui.tableWidget.setColumnWidth(col_j, 150)
              self.ui.tableWidget.setRowHeight(row_i, 150)
          self.IsStore+=1
        
    def hideHorizontallHeader(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.ui.tableWidget.horizontalHeader().setVisible(False)
        self.IsStore+=1
        
    def showHorizontallHeader(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.ui.tableWidget.horizontalHeader().setVisible(True)
        self.IsStore+=1
        
    def hideVerticalHeader(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.ui.tableWidget.verticalHeader().setVisible(False)
        self.IsStore+=1
        
    def showVerticalHeader(self):
        if(self.IsStore==1):
            self.IsStore=0
            return
        self.ui.tableWidget.verticalHeader().setVisible(True)
        self.IsStore+=1
        

    def save_group(self):
        if(self.IsStore>=1):
            self.IsStore=0
            return
        if self.save_worker is not None and self.save_worker.isRunning():
            QMessageBox.information(self, "保存中", "分類結果正在背景保存，請稍候。")
            return
        if not class_list.CF_list:
            QMessageBox.warning(self, "提示", "目前沒有分組結果可以保存。")
            return

        now = datetime.now()
        current_time = now.strftime(" %m %d %Y %H %M %S")
        download_dir = os.path.join(str(downloads_dir()), "Classification" + current_time)
        groups_snapshot = self._save_snapshot()
        total = sum(len(group["images"]) for group in groups_snapshot)
        if total == 0:
            QMessageBox.warning(self, "提示", "目前沒有可保存的圖片。")
            return

        self.save_progress.setRange(0, total)
        self.save_progress.setValue(0)
        self.save_progress.setVisible(True)
        self.ui.action_11.setEnabled(False)
        self.ui.statusBar.showMessage("Saving 0/" + str(total) + " images...")

        self.save_worker = SaveGroupsWorker(groups_snapshot, download_dir, self)
        self.save_worker.progress.connect(self._save_progress)
        self.save_worker.finished.connect(self._save_finished)
        self.save_worker.failed.connect(self._save_failed)
        self.save_worker.start()

    def _save_snapshot(self):
        groups_snapshot = []
        group_count = len(class_list.CF_list)
        group_number_width = max(2, len(str(group_count)))
        for group_index, group in enumerate(class_list.CF_list, start=1):
            group_name = "Group" + str(group_index).zfill(group_number_width)
            images = []
            for buf_img in group.same:
                images.append({
                    "source_path": buf_img.name,
                    "filename": buf_img.filename,
                })
            groups_snapshot.append({"name": group_name, "images": images})
        return groups_snapshot

    def _save_progress(self, done, total, group_name):
        self.save_progress.setMaximum(total)
        self.save_progress.setValue(done)
        self.ui.statusBar.showMessage("Saving " + str(done) + "/" + str(total) + " images to " + group_name + "...")

    def _save_finished(self, output_root, saved, total, errors):
        self.save_progress.setVisible(False)
        self.ui.action_11.setEnabled(True)
        self.save_worker = None
        message = "保存完成：" + str(saved) + "/" + str(total) + " 張圖片\n" + output_root
        if errors:
            message += "\n\n略過 " + str(len(errors)) + " 張：\n" + "\n".join(errors[:8])
        self.ui.statusBar.showMessage("Saved to " + output_root, 8000)
        reply = QMessageBox.information(
            self,
            "保存完成",
            message + "\n\n是否打開保存資料夾？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes and hasattr(os, "startfile"):
            os.startfile(output_root)

    def _save_failed(self, message):
        self.save_progress.setVisible(False)
        self.ui.action_11.setEnabled(True)
        self.save_worker = None
        self.ui.statusBar.showMessage("Save failed", 5000)
        QMessageBox.warning(self, "保存失敗", message)
    
    def readFile(self):
      
        print("read file  ")
        start=time.time()
        image_files = iter_image_files(default_open_dir())
        del img[:]
        for image_path in image_files:
            try:
                buf=IMG(str(image_path),image_path.name)
                buf.img_shape()
                buf.create_sift()
                img.append(buf)
            except Exception as exc:
                print("skip image:", image_path, exc)
        end=time.time()


        total_input_time=end-start
        print("total input time : ",total_input_time)
        print("\n\n\n")
        
        for i in img:
            print(i.name)
        print("\n\n\n")
    
    def openFile(self):
       # self.clicked_counter += 1
        #print(f"You clicked {self.clicked_counter} times.")
        if(self.IsStore>=1):
            self.IsStore=0
            return
        filepath = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", default_open_dir())
        if not filepath:
            return
        print(filepath)
        self.IsStore+=1
    
    
    
    def IMG_match(self):
        if len(img) == 0:
            QMessageBox.warning(self, "提示", "還沒有可匹配的圖片，請先讀取圖片。")
            return
        start=time.time()

        img_len=len(img)
    
        list_classification=[]
        for i in range(len(img)):
    
            #print("img name : ",img[i].filename)
            IsClass=False
            for index in range(len(list_classification)):
                IsSame , IsBig=sift_ahash(img[i],list_classification[index].same[0])
                if(IsSame):
                    IsClass=True
                    list_classification[index].save_img(img[i],IsBig)
                    if(IsBig):
                        pop_list=[]
                        for buf_index in range(index+1,len(list_classification)):
                            buf_Same,buf_Big=sift_ahash(list_classification[buf_index].same[0],list_classification[index].same[0])
                            if(buf_Same & (buf_Big==False)):
                                #print("================RE_Group==============")
                                list_classification[index].union(list_classification[buf_index])
                                pop_list.append(buf_index)
                        for idx in sorted(pop_list, reverse = True):
                            del list_classification[idx]
    
                    break
    
            if not(IsClass):
                buf = classification(img[i])
                list_classification.append(buf)
            #PRINT_GROUP(list_classification)
    
        del img[:]
    
        end=time.time()
        classification_time = end - start
        print("classification input time : ",classification_time)
    
    
    
        #now = datetime.now()
        #current_time = now.strftime("%H_%M_%S")
       # path='D:/source/vscode/python_project/classificaton'+'_'+str(current_time)+'.txt'
       #path='D:/classificaton.txt'
       #f=open(path,'w')
       
       
    
        group_index=0
        for tem_class in list_classification:
            buf=[]
            if(group_index<10):
                group_string='Group'+str(group_index)+"  : "
            else:
                group_string='Group'+str(group_index)+" : "
    
            buf.append(group_string)
            for buf_img in tem_class.same:
                buf.append(buf_img.filename)
                buf.append(" ")
            buf.append('\n')
            print(buf)
            #f.writelines(buf)
            group_index+=1
       # f.close()

        print("end")
    
