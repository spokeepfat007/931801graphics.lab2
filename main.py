import sys

import numpy as np
from matplotlib import image as img
import design
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import math
import os
# This is a sample Python script.
from PIL import ImageQt
from PIL import Image as im


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.function = 0
        self.v=0
        self.a=[]
        self.width = 961
        self.height = 591
        self.imagePath = 'круги.jpg'
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.radioButton.toggled.connect(self._on_radio_button_clicked)
        self.radioButton_2.toggled.connect(self._on_radio_button_clicked)
        self.pushButton.clicked.connect(self.on_click)
        self.pushButton_2.clicked.connect(self.on_click2)
        self.pushButton_3.clicked.connect(self.on_click3)
        self.label.setScaledContents(True)
        pixmap = QPixmap('круги.jpg')
        pixmap = pixmap.scaled(300, 400, QtCore.Qt.KeepAspectRatio)
        self.pixmap=pixmap
        self.label.setPixmap(pixmap)
        self.NumOfCopies = 6;
        self.label.move(100, 100)

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(qRgba(255, 255, 255,255))

    @pyqtSlot()
    def on_click(self):
        image = QFileDialog.getOpenFileName(None, 'OpenFile', '', "Image file(*.jpg)")
        self.imagePath = image[0]
        pixmap = QPixmap(self.imagePath)
        self.pixmap=pixmap
        pixmap = pixmap.scaled(300, 400, QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        self.label.adjustSize()
        self.v=0
        self.a=[]
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(qRgba(255, 255, 255,255))

    @pyqtSlot()
    def on_click2(self):
        self.v=0
        self.a=[]
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(qRgba(255, 255, 255,255))
        self.label.clear()
        self.update()

    @pyqtSlot()
    def on_click3(self):
        pixmap = QPixmap(self.imagePath)
        pixmap = pixmap.scaled(300, 400, QtCore.Qt.KeepAspectRatio)
        self.pixmap=pixmap
        self.label.setPixmap(pixmap)
        self.label.adjustSize()
        self.v=0
        self.a=[]
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(qRgba(255, 255, 255,255))
        self.update()

    def _on_radio_button_clicked(self):
        button = self.sender()
        text=button.text()
        self.function = self.TextCatch(text)

    def TextCatch(self,text):
        if text=='Simple':
            return 0
        if text=='Bilinear/Trilinear':
            return 1

    def setLabels(self, x):
        # pixmap = QPixmap(self.label.pixmap().toImage())
        # pixmap.fill(Qt.transparent)
        qp = QPainter(self.pixmap)
        pen = QPen(Qt.green, 5)
        qp.setPen(pen)
        qp.drawPoint(x.x()-100,x.y()-100)
        self.label.setPixmap(self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
             if self.v<6:
                painter = QPainter(self.image)
                painter.setPen(QPen(Qt.darkGreen, 5, Qt.SolidLine))
                self.a += [event.pos().x()-100 if self.v<3 else event.pos().x()-481, event.pos().y() - 100 if self.v<3 else event.pos().y()]
                painter.drawPoint(event.pos())
                if (self.v<3):
                    self.setLabels(event.pos())
                self.update()
                self.v+=1
             elif self.v==6:
                 self.nonlinearSolver()


    def findImageBorders(self, matrix):
        a1 = np.array([0,0,1]).dot(matrix)
        a2 = np.array([self.label.width()-1,0 , 1]).dot(matrix)
        a3 = np.array([0,self.label.height()-1,1]).dot(matrix)
        a4 = np.array([self.label.width()-1,self.label.height()-1 , 1]).dot(matrix)
        mas = [a1,a2,a3,a4]
        # print(a1,a2,a3,a4, sep='\n')
        minX = min(mas[i][0] for i in range(4))
        minY = min(mas[i][1] for i in range(4))
        maxX = max(mas[i][0] for i in range(4))
        maxY = max(mas[i][1] for i in range(4))
        minX, minY, maxX, maxY, interX, interY = self.findScreenBorders(matrix,[minX,minY,maxX, maxY])

        return minX,minY, maxX, maxY, interX, interY

    def switch(self,value, PointsMax, PointsMin, max,min,c,a):
        if value[0]==0:
            inter = int(((c/a)-(max-min))/2)
            return min, max, inter
        if value[0] == 1 and value[1]==1:
            min=PointsMin
            max=PointsMin+ c/a

            return min, max, 0
        elif value == [1,0,1,1]:
            min = PointsMin-(c/a-(PointsMax-PointsMin))/2
            max = PointsMax+(c/a-(PointsMax-PointsMin))/2
            return min, max, 0
        elif value == [1,0,1,0]:
            max = PointsMax+(c/a-(PointsMax-PointsMin)) - (PointsMin-min)
            return min, max, 0
        elif value ==[1,0,0,1]:
            min = PointsMin-(c/a-(PointsMax-PointsMin)) - (max-PointsMax)
            return min, max, 0
        else:
            return min, max, 0

    def findScreenBorders(self, matrix, imageBorders):
        minX, minY, maxX, maxY = imageBorders
        NewPoint1 = np.array([self.a[0],self.a[1],1]).dot(matrix)
        NewPoint2 = np.array([self.a[2],self.a[3],1]).dot(matrix)
        NewPoint3 = np.array([self.a[4],self.a[5],1]).dot(matrix)
        PointsMaxX =max(NewPoint1[0],NewPoint2[0],NewPoint3[0])
        PointsMaxY = max(NewPoint1[1],NewPoint2[1],NewPoint3[1])
        PointsMinX =min(NewPoint1[0],NewPoint2[0],NewPoint3[0])
        PointsMinY = min(NewPoint1[1],NewPoint2[1],NewPoint3[1])
        value = [((maxX-minX)>(self.width/2)),(PointsMaxX-PointsMinX)>self.width/2,(self.width/2-(PointsMaxX-PointsMinX))/2<(maxX-PointsMaxX),(self.width/2-(PointsMaxX-PointsMinX))/2<(PointsMinX-minX)]
        minX, maxX, interX = self.switch(value,PointsMaxX, PointsMinX, maxX,minX,self.width,2)
        value = [(maxY-minY)>self.height,(PointsMaxY-PointsMinY)>self.height,(self.height-(PointsMaxY-PointsMinY))<(maxY-PointsMaxY),(self.height-(PointsMaxY-PointsMinY))<(PointsMinY-minY)]
        minY, maxY, interY= self.switch(value,PointsMaxY, PointsMinY, maxY,minY,self.height,1)
        return minX, minY, maxX, maxY, interX, interY

    def simpleTransformation(self, imageBorders, ObrMatrix, painter, image_data):
        minX, minY, maxX, maxY, interX, interY = imageBorders
        for i in range(int(minX),int(maxX)):
            for j in range(int(minY), int(maxY)):
                z = np.array([i, j, 1]).dot(ObrMatrix)
                if ((z[0]<0) or (z[0]>(self.label.width()-1)) or (z[1]<0) or (z[1] > (self.label.height()-1))):
                    painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
                else:
                    r, g, b = image_data[int(z[1])*self.label.width()+int(z[0])]
                    painter.setPen(QPen(QColor(r,g,b), 1, Qt.SolidLine))
                painter.drawPoint(i+481-int(minX)+interX, j+1-int(minY)+interY)
                self.update()

    def bilinearFiltr(self, imageBorders, ObrMatrix, painter, image_data):
        minX, minY, maxX, maxY, interX, interY = imageBorders
        for i in range(int(minX),int(maxX),1):
            for j in range(int(minY), int(maxY),1):
                z = np.array([i, j, 1]).dot(ObrMatrix)
                if ((z[0]<0) or (z[0]>(self.label.width()-1)) or (z[1]<0) or (z[1] > (self.label.height()-1))):
                    painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
                else:
                    r,g,b = (np.float_(image_data[math.ceil(z[1])*self.label.width()+math.ceil(z[0])])*(z[0]-math.floor(z[0])) +
                             np.float_(image_data[math.ceil(z[1])*self.label.width()+math.floor(z[0])])*(math.ceil(z[0])-z[0]))*(z[1]-math.floor(z[1])) + \
                            (np.float_(image_data[math.floor(z[1])*self.label.width()+math.ceil(z[0])])*(z[0]-math.floor(z[0])) +
                             np.float_(image_data[math.floor(z[1])*self.label.width()+math.floor(z[0])])*(math.ceil(z[0])-z[0]))*(math.ceil(z[1])-z[1])
                   #r, g, b = [round(i) for i in([r,g,b])] #Целочисленное округление, если нужно
                    painter.setPen(QPen(QColor(r,g,b), 1, Qt.SolidLine))
                painter.drawPoint(i+481-int(minX)+interX, j+1-int(minY)+interY)
                self.update()

    def trilinearFiltr(self, imageBorders, ObrMatrix, painter, image_data, image):
        minX, minY, maxX, maxY, interX, interY  = imageBorders
        matrixes=[image_data]
        # for i in range(1, self.NumOfCopies):
        #     power = pow(2,i)
        #     matrixes+=[image.resize((math.ceil(self.label.size().width()/power), math.ceil(self.label.size().height()/power))).getdata()]
        for power in range(1, self.NumOfCopies):
            power = pow(2,power)
            new_picture=[]
            for j in range(0, self.label.height(), power):
                for i in range(0, self.label.width(), power):
                    s= np.zeros(shape=3)
                    maxi=power if ((self.label.width()-power)>=i)else (self.label.width()-i)
                    maxj=power if ((self.label.height()-power)>=j) else (self.label.height()-j)
                    for i1 in range(0,maxi):
                        for i2 in range(0,maxj):
                            s+=np.array(image_data[(j+i2)*self.label.width()+(i1+i)])
                    for i1 in range(0,3):
                        s[i1]/=maxi*maxj
                    new_picture+=[s]
            matrixes+=[new_picture]

        for i in range(int(minX),int(maxX)):
            for j in range(int(minY), int(maxY)):
                z = np.array([i, j, 1]).dot(ObrMatrix)
                if ((z[0]<0) or (z[0]>(self.label.width()-1)) or (z[1]<0) or (z[1] > (self.label.height()-1))):
                    painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
                else:
                    distance = np.array([i+1, j, 1]).dot(ObrMatrix)-np.array([i, j, 1]).dot(ObrMatrix)
                    K = (abs(distance[0])+abs(distance[1]))/2
                    m=0
                    if (K>=math.pow(2,self.NumOfCopies-1)):
                        K=math.pow(2,self.NumOfCopies-1)
                    elif(K<=1):
                        K=1
                    if K<=2:
                        m=0
                    else:
                        m = math.ceil(math.log2(K))-1

                    Im = (np.float_(matrixes[m][math.ceil(z[1])//pow(2,m)*math.ceil(self.label.width()/pow(2,m))+int(math.ceil(z[0])/pow(2,m))])*(z[0]-math.floor(z[0])) +
                             np.float_(matrixes[m][math.ceil(z[1])//pow(2,m)*math.ceil(self.label.width()/pow(2,m))+int(math.floor(z[0])/pow(2,m))])*(math.ceil(z[0])-z[0]))*(z[1]-math.floor(z[1])) + \
                            (np.float_(matrixes[m][math.floor(z[1])//pow(2,m)*math.ceil(self.label.width()/pow(2,m))+int(math.ceil(z[0])/pow(2,m))])*(z[0]-math.floor(z[0])) +
                             np.float_(matrixes[m][math.floor(z[1])//pow(2,m)*math.ceil(self.label.width()/pow(2,m))+int(math.floor(z[0])/pow(2,m))])*(math.ceil(z[0])-z[0]))*(math.ceil(z[1])-z[1])
                    Im=matrixes[m][int(z[1]/pow(2,m))*math.ceil(self.label.width()/pow(2,m))+int(z[0]/pow(2,m))]
                    I2m = (np.float_(matrixes[m+1][int(math.ceil(z[1])//(2*pow(2,m)))*math.ceil(self.label.width()/(2*pow(2,m)))+int(math.ceil(z[0])/(2*pow(2,m)))])*(z[0]-math.floor(z[0])) +
                          np.float_(matrixes[m+1][int(math.ceil(z[1])//(2*pow(2,m)))*math.ceil(self.label.width()/(2*pow(2,m)))+int(math.floor(z[0])/(2*pow(2,m)))])*(math.ceil(z[0])-z[0]))*(z[1]-math.floor(z[1])) + \
                         (np.float_(matrixes[m+1][int(math.floor(z[1])//(2*pow(2,m)))*math.ceil(self.label.width()/(2*pow(2,m)))+int(math.ceil(z[0])/(2*pow(2,m)))])*(z[0]-math.floor(z[0])) +
                          np.float_(matrixes[m+1][int(math.floor(z[1])//(2*pow(2,m)))*math.ceil(self.label.width()/(2*pow(2,m)))+int(math.floor(z[0])/(2*pow(2,m)))])*(math.ceil(z[0])-z[0]))*(math.ceil(z[1])-z[1])
                    #I2m=matrixes[m+1][int(z[1]/(2*pow(2,m)))*math.ceil(self.label.width()/(2*pow(2,m)))+int((z[0])/(2*pow(2,m)))]
                    color=[]
                    for rad in range(0,3):
                        color+=[(Im[rad]*(2*pow(2,m)-K)+I2m[rad]*(K-pow(2,m)))/pow(2,m)]
                    painter.setPen(QPen(QColor(color[0],color[1],color[2]), 1, Qt.SolidLine))
                painter.drawPoint(i+481-int(minX)+interX, j+1-int(minY)+interY)
                self.update()

    def IncreaseDecrease(self,matrix,obrmatr):
        distance = np.array([self.a[0],self.a[1],1])-(np.array([self.a[0],self.a[1],1]).dot(matrix)+np.array([1,0,0])).dot(obrmatr)
        K = (abs(distance[0])+abs(distance[1]))/2
        if K>=1:
            return "decrease"
        else:
            return "increase"

    def nonlinearSolver(self):
        #print(self.imagePath)
        image = im.open(self.imagePath)
        image = image.resize((self.label.size().width(), self.label.size().height()))
        #image.show()
        image_data = image.getdata()
        #self.a=[34, 316, 122, 83, 183, 324, 113, 240, 138, 198, 139, 238]
        a5 = np.array([[self.a[i-i%2+j if i%2==0 else i-i%2+j-3] if j<2 and i%2==0 or j>2 and j<5 and i%2==1 else 1 if j==2 and i%2==0 or j==5 and i%2==1 else 0 for j in range(6)] for i in range(6)])
        v5 = np.array([self.a[6+i] for i in range(6)])
        # print(v5, a5, sep='\n')

        result = np.linalg.solve(a5, v5)
        matrix = np.array([[result[3*i+j] if i<2 else 0 if j<2 else 1 for j in range(3)] for i in range(3)]).transpose()
        # print(matrix)

        #Проверка
        # a1 = np.array([self.a[0],self.a[1], 1])
        # total = a1.dot(matrix)
        # print(total)
        #Поиск обратной матрицы
        ObrMatrix = np.linalg.inv(matrix)
        # a = np.array([self.a[6], self.a[7], 1])
        # print(a.dot(ObrMatrix))
        painter = QPainter(self.image)

        #Поиск прямоугольника
        # for index2 in range(self.label.width()):
        #     for index1 in range(self.label.height()):
        #         r, g, b = image_data[index1*self.label.width()+index2]
        #         painter.setPen(QPen(QColor(r,g,b), 1, Qt.SolidLine))
        #         painter.drawPoint(index2+481, index1+1)
        #         self.update()

        #Поиск границ полученного изображения
        imageBorders = self.findImageBorders(matrix)
        way = self.IncreaseDecrease(matrix,ObrMatrix)
        if self.function==0:
            self.simpleTransformation(imageBorders, ObrMatrix, painter, image_data)
        else:
            if (way=="increase"):
                self.bilinearFiltr(imageBorders, ObrMatrix, painter, image_data)
            else:
                self.trilinearFiltr(imageBorders, ObrMatrix, painter, image_data, image)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawLine(481,0,481,700)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение