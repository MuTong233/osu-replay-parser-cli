#!/usr/bin/env python3
# WebUI实现
# 开发要点：

# 必须继承QObject并写好init函数
# 凡是『导出』给javascript的函数，需要加pyqtSlot修饰器。
# 与其他QObject交互仍然可以使用pyqtSignal

# Requirements:
# pip3 install pyqt5 -U

from PyQt5.QtCore import *

class MyObjectCls(QObject):
    sigSetParentWindowTitle = pyqtSignal(str)
    
    def __init__(self,parent=None):
        QObject.__init__(self,parent)
    @pyqtSlot(str)
    def consolePrint(self,msg):
        print(msg)
    @pyqtSlot(str)
    def setParentWindowTitle(self,msg):
        self.sigSetParentWindowTitle.emit(msg)
    @pyqtSlot(str,str)
    def saveFile(self,content,fileName):
        with open(str(fileName),"w") as fp:
            fp.write(str(content))