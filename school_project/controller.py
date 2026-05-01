# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 16:16:51 2022

@author: User
"""

from PyQt5 import QtWidgets, QtGui, QtCore
from widget import Ui_Form
#from PyQt5.QtGui import QImage, QPixmap
#from PyQt5.QtWidgets import QProgressBar
import cv2
import time
#from concurrent.futures import thread
#from ctypes import BigEndianStructure
import os
#from random import shuffle
#from tokenize import group
#from turtle import down, up
import numpy as np
#import pandas as pd
#from matplotlib import pyplot as plt
import math
from math import *
#from datetime import datetime
from PyQt5.QtCore import Qt, QMimeData, QDate, QDateTime, QTime, QStringListModel, QSize,QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QImage, QPainter, QBrush, QPixmap, QStandardItemModel, QStandardItem, QColor, QFont
from PyQt5.QtPrintSupport import QPageSetupDialog, QPrinter
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QFormLayout, QLabel, QLineEdit, QPushButton, QGridLayout, \
    QCalendarWidget, QVBoxLayout, QDateTimeEdit, QAction, QMainWindow, QTextEdit, QStatusBar, QFileDialog, QDialog, \
    QTableView, QMessageBox, QListView, QListWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView

from controller2 import MainWindow_controller2

import class_list
from app_paths import debug_output_dir, default_open_dir
from image_utils import iter_image_files



class Thread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(Thread, self).__init__()

    def __del__(self):
        self.wait()
    ''' not used
    def run(self,directory_name):
        for i in range(100):
            time.sleep(0.01)
            self._signal.emit(i)
    '''
    ''' not used
    def thread_read_directory(self,directory_name): #check
        print("read file  ")
        start=time.time()

            #D:/source/vscode/python_project/test_file
            #C:/Users/howar/Downloads/differ_size


        count=0
        len_img=len(os.listdir(directory_name))
        print("len img : ",len_img)
        for filename in os.listdir(directory_name):
            
            name_string = (directory_name + "/" + filename)
            #print("img path : ",name_string)
            buf=IMG(name_string,filename)
            buf.img_shape()
            buf.create_sift()
            img.append(buf)
            buf_index=int(count/len_img*100)
            print("buf_index : ",buf_index)
            self._signal.emit(buf_index)
            count+=1
            print("\n\n")
            #read_directory("D:/test_img")

        self._signal.emit(100)
               
        end=time.time()


        total_input_time=end-start
        print("total input time : ",total_input_time)
        print("\n\n\n")
      
    def thread_match_img():
        return 0
    '''  
def new_resize_img(img, new_scale):                 #check

    height, width = img.shape[:2]
    scale = new_scale
    try:
        buf_img = cv2.resize(img, (int(scale*width), int(scale*height)),interpolation=cv2.INTER_AREA)
    except:
        return img
    return buf_img


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
    qt_image = qt_image.convertToFormat(QImage.Format_RGB888)
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


'''     not used
def read_directory(directory_name): #check

   for filename in os.listdir(directory_name):

        name_string = (directory_name + "/" + filename)
        print("img path : ",name_string)
        buf=IMG(name_string,filename)
        buf.img_shape()
        buf.create_sift()
        img.append(buf)
   print("\n\n")
#button_show=True

'''

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
        #buf=buf_classification.same.pop()
        self.same+=buf_classification.same
        #self.same.insert(0,buf)
        self.img_count+=buf_classification.img_count

    def PRINT_GROUP(self):
        print("\n")

        print("Group  : ",end="")
        for buf in self.same:
                print(buf.filename," ",end="")
        print("")
        print("\n")



def PRINT_GROUP(buf_list):                      #check
    print("\n")
    for i in range(len(buf_list)):
        print("Group ",i," : ",end="")
        for buf in buf_list[i].same:
            print(buf.filename," ",end="")
        print("")
    print("\n")

class Form_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setup_control()
        
       

    def setup_control(self):
        # TODO
       # self.ui.progressBar.setValue(0)
        self.ui.pushButton.setText("選擇資料夾")
       # self.clicked_counter = 0
        self.ui.pushButton.clicked.connect(self.openFile)
        self.ui.pushButton_2.clicked.connect(self.readFile)
        self.ui.pushButton_3.clicked.connect(self.IMG_match)
        self.ui.pushButton_4.clicked.connect(self.cancelReadFile)
        if hasattr(self.ui, "previewListWidget"):
            self.ui.listWidget.currentTextChanged.connect(self.updatePreview)
       # self.ui.listWidget.clicked.connect(self.ui.listWidget.currentItem().text())

    def cancelReadFile(self):
        start=time.time()
        self.ui.pushButton_2.setEnabled(True)
        
        #self.ui.pushButton_3.setEnabled(False)
        del img[:]
        end=time.time()
        classification_time = end - start
        print("classification input time : ",classification_time)
        print("end")
        
            
    def openFile(self):
       # self.clicked_counter += 1
        #print(f"You clicked {self.clicked_counter} times.")
       filepath = QFileDialog.getExistingDirectory(self, "请选择文件夹路径", default_open_dir())
       if not filepath:
           return
       print(filepath)
       self.ui.listWidget.addItem(filepath)
       self.ui.listWidget.setCurrentRow(self.ui.listWidget.count() - 1)
       self.updatePreview(filepath)
       
    def updatePreview(self, directory_name):
        if not hasattr(self.ui, "previewListWidget") or not directory_name:
            return
        self.ui.previewListWidget.clear()
        for image_path in iter_image_files(directory_name)[:12]:
            pixmap = QPixmap(str(image_path))
            if pixmap.isNull():
                continue
            icon = QIcon(pixmap.scaled(92, 92, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            item = QtWidgets.QListWidgetItem(icon, image_path.name)
            item.setToolTip(str(image_path))
            self.ui.previewListWidget.addItem(item)
        if self.ui.previewListWidget.count() == 0:
            self.ui.previewListWidget.addItem("沒有可預覽的圖片")
        else:
            self.ui.previewListWidget.addItem("...")
       
       
    def readFile(self):
        #self.ui.pushButton_3.setEnabled(False)
        #time.sleep(1)
        current_item = self.ui.listWidget.currentItem()
        if current_item is None:
            QMessageBox.warning(self, "提示", "請先選擇圖片資料夾。")
            return
        filepath = current_item.text()
        self.thread = Thread()
        self.thread._signal.connect(self.signal_accept)
        
        #self.thread.thread_read_directory(filepath)
        
        
        
        print("read file  ")
        start=time.time()

            #D:/source/vscode/python_project/test_file
            #C:/Users/howar/Downloads/differ_size

        directory_name=filepath
        count=0
        image_files = iter_image_files(directory_name)
        len_img=len(image_files)
        if len_img == 0:
            QMessageBox.warning(self, "提示", "這個資料夾沒有可掃描的圖片。")
            return
        print("len img : ",len_img)
        del img[:]
        for image_path in image_files:
            
            name_string = str(image_path)
            print("img path : ",name_string)
            try:
                buf=IMG(name_string,image_path.name)
                buf.img_shape()
                buf.create_sift()
                img.append(buf)
            except Exception as exc:
                print("skip image:", name_string, exc)
            buf_index=int(count/len_img*100)
            #print("buf_index : ",buf_index)
            self.thread._signal.emit(buf_index)
            count+=1
            #print("\n\n")
            #read_directory("D:/test_img")

        self.thread._signal.emit(100)
               
        end=time.time()


        total_input_time=end-start
        print("total input time : ",total_input_time)
        print("\n\n\n")
        
  #      self.ui.pushButton_2.setEnabled(False)
        
        
        
        
        
        
        #self.ui.pushButton_3.setEnabled(True)
        
        
        
    def signal_accept(self, msg):
        self.ui.progressBar.setValue(int(msg))
        if self.ui.progressBar.value() == 99:
            self.ui.progressBar.setValue(0)
            self.ui.pushButton_2.setEnabled(True)
            
    def IMG_match(self):
        
        if len(img) == 0:
            QMessageBox.warning(self, "提示", "還沒有可匹配的圖片，請先開始掃描。")
            return
        
        start=time.time()
        

        img_len=len(img)
    
        list_classification=[]
    
        #self._signal.emit(100)
        self.thread._signal.emit(0)
        scalar=0
        progress_step=max(1, img_len//4)
        for i in range(img_len):
            buf_index=i/img_len*100
            self.thread._signal.emit(buf_index)    
            if((i%progress_step)==0):
                percent=scalar*25
                scalar+=1
                print("working ",percent," % ......")
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
        self.thread._signal.emit(100)
        del img[:]
    
        end=time.time()
        classification_time = end - start
        print("classification input time : ",classification_time)
    
    
    
        #now = datetime.now()
        #current_time = now.strftime("%H_%M_%S")
       # path='D:/source/vscode/python_project/classificaton'+'_'+str(current_time)+'.txt'
       #path='D:/classificaton.txt'
       #f=open(path,'w')
       
       
        print("\n\nmatch result\n\n")
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
        list_classification=sorted(list_classification, key = lambda s: s.img_count)
        class_list.CF_list=list_classification
        if class_list.CF_list:
            print("global group 0 img 0 filename : ",class_list.CF_list[0].same[0].filename)#第一个0是第0群，same是第0群里面第0个照片，简短路径
        #item = QtWidgets.QTableWidgetItem(QIcon(path),filename)
        print("\n\nend")
       
        
        self.window = MainWindow_controller2()
        self.window.show()
        self.ui.pushButton_2.setEnabled(True)
        
    

    

        
        


  
    
