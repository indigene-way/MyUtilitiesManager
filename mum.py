#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import shutil
import re 
import uuid
import time
import math
import random
import datetime
from datetime import datetime
import zipfile

import sqlite3
from PyQt5.QtSql import *

from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

#============================================================================================================DATA BASE
conn = sqlite3.connect('db.db')
# os.system("icacls db.db /grant *S-1-1-0:(D,WDAC)")	
query = conn.cursor()

#===========================================================================Vehicules 
# query.execute("DROP TABLE Progs")
try:
    query.execute("SELECT id FROM Progs ORDER BY id DESC")

except:
    conn.execute("""CREATE TABLE Progs (
					id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
					prog_name VARCHAR(100) ,
					prog_state VARCHAR(12),
					prog_path VARCHAR(12),
					prog_date DATETIME )""")


# =============GLOBAL TIME VARIABLES
dateIndicator = time.strftime("%Y %m %d")

#REPOSITORIES 
dev = "Developper"
util = "Utilities"     
media = "Media"  

class MessageFactory():

	def Done(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setWindowTitle("Success !")
		msg.setText("operation done succefully.")
		msg.exec_()	      
# =============UI CLASS Widget Rename Dialog		
qtANPRW= "DESIGN/RenameDialog.ui"
Ui_RenameDialog, QtBaseClass = uic.loadUiType(qtANPRW)	
class RenameDialog(QDialog, Ui_RenameDialog):#EDIT : MODIF Product Name,Price DIALOG
	
    def __init__(self):
        QDialog.__init__(self)
        Ui_RenameDialog.__init__(self)
        self.setupUi(self)	
        self.setWindowTitle("Rename Folder Dialog.")
        
# =============UI CLASS DIALOG		
qtANPR= "DESIGN/main.ui"
Ui_Main, QtBaseClass = uic.loadUiType(qtANPR)	
class Anpr(QDialog, Ui_Main):#EDIT : MODIF Product Name,Price DIALOG
	
    def __init__(self):
        QDialog.__init__(self)
        Ui_Main.__init__(self)
        self.setupUi(self)
        
        self.show()
        self.setWindowTitle("My Utilities Manager.")
        
        # INSTANCE
        self.namer = RenameDialog()
        self.mf = MessageFactory()
        
        self.dateTime = time.strftime("%d-%m-%Y      %H:%M:%S")
        # self.now = time.strftime("%H:%M:%S")
        self.actualPath = ""
        now = datetime.now()
        self.current_time = now.strftime("%H:%M:%S")
        
        self.TableWidgetInit()#TABLE WIDGET DEFAULT
        
        #SIGNAL menu
        self.menu1.clicked.connect(self.Menu1)
        self.menu2.clicked.connect(self.Menu2)
        self.menu3.clicked.connect(self.Menu3)
        self.menu4.clicked.connect(self.Menu4)
        
        self.install.clicked.connect(self.Install)    
        self.addFolder.clicked.connect(self.AddFolder)    
        self.deleteFolder.clicked.connect(self.DeleteFolder)  
        self.renameF.clicked.connect(self.RenameFolder)  
        self.zipFolder.clicked.connect(self.Unzip)  
        
        self.allFolders.clicked.connect(self.AllFolders)    
        
    def TableWidgetInit(self):
        #CLEAN TABLE WIDGET
        self.tableWidget.clear()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0) 

    def MenuProto(self, path):
        self.processndicator.setText("")
        
        #CLEAN TABLE WIDGET
        self.tableWidget.clear()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 560)
        
        self.tableWidget.setHorizontalHeaderLabels(['Connection','Path', 'Programme'])
        self.header = self.tableWidget.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignHCenter) 
        
        #GETTING FILES
        entries = os.listdir(path)
        for entry in entries:
            #GET INFO FROM DATA
            query.execute("SELECT prog_state FROM Progs WHERE prog_name='"+entry+"' \
            ORDER BY id ASC")
            state = query.fetchone()
            
            self.rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(self.rowPosition)
            if str(state).strip("(',')") != "None":
                self.tableWidget.setItem(self.rowPosition , 0, QTableWidgetItem(str(state).strip("(',')")))
            else :
                self.tableWidget.setItem(self.rowPosition , 0, QTableWidgetItem("Uninstalled"))
            self.tableWidget.setItem(self.rowPosition , 1, QTableWidgetItem(path))
            self.tableWidget.setItem(self.rowPosition , 2, QTableWidgetItem(str(entry)))

    def Menu1(self):#ANPR SYS
        
        self.indicator.setText("Developpement")
        icon = "IMAGES/Icons/dev.png"
        self.iconIndicator.setIcon(QIcon(icon))
        self.MenuProto("EXE\\"+dev)
        self.actualPath = dev
           
    def Menu2(self):#PARKED CARS
        
        self.indicator.setText("Utilities")
        icon = "IMAGES/Icons/util.png"
        self.iconIndicator.setIcon(QIcon(icon))
        self.MenuProto("EXE\\"+util)
        self.actualPath = util
    
    def Menu3(self):
        self.indicator.setText("Medias")
        icon = "IMAGES/Icons/media.png"
        self.iconIndicator.setIcon(QIcon(icon))
        self.MenuProto("EXE\\"+media)
        self.actualPath = media
    
    def Menu4(self):
        self.indicator.setText("My List")
        icon = "IMAGES/Icons/mylist.png"
        self.iconIndicator.setIcon(QIcon(icon))
        # self.MenuProto("EXE\\"+media)
        # actualPath = dev
        self.processndicator.setText("")
        
        #CLEAN TABLE WIDGET
        self.tableWidget.clear()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 420)
        self.tableWidget.setColumnWidth(3, 100)
        
        # GETTING DATA SELECT 
        self.cur = query
        self.cur.execute("SELECT DISTINCT prog_date,prog_path,prog_name,prog_state FROM Progs \
        ORDER BY id ASC")
        
        self.tableWidget.setHorizontalHeaderLabels(['Date', 'Path','Programme','State'])
        self.header = self.tableWidget.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignHCenter) 
        
        #GETTING FILES
        for row, form in enumerate(self.cur):
            self.tableWidget.insertRow(row)
            for column, item in enumerate(form):    
                self.tableWidget.setItem(row, column,QTableWidgetItem(str(item)))
 
    def AllFolders(self):
        self.processndicator.setText("")
        self.indicator.setText("All Folders")
        
        #CLEAN TABLE WIDGET
        self.tableWidget.clear()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 660)
        
        self.tableWidget.setHorizontalHeaderLabels(['Path', 'Programme'])
        self.header = self.tableWidget.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignHCenter) 
        
        #GETTING FILES
        entries = os.listdir("EXE\\"+dev)
        for entry in entries:
            self.rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(self.rowPosition)
            #self.tableWidget.setSortingEnabled(True)
            self.tableWidget.setItem(self.rowPosition , 0, QTableWidgetItem(dev))
            self.tableWidget.setItem(self.rowPosition , 1, QTableWidgetItem(str(entry))) 
        
        #GETTING FILES
        entries = os.listdir("EXE\\"+util)
        for entry in entries:
            self.rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(self.rowPosition)
            #self.tableWidget.setSortingEnabled(True)
            self.tableWidget.setItem(self.rowPosition , 0, QTableWidgetItem(util))
            self.tableWidget.setItem(self.rowPosition , 1, QTableWidgetItem(str(entry))) 
        
        #GETTING FILES
        entries = os.listdir("EXE\\"+media)
        for entry in entries:
            self.rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(self.rowPosition)
            #self.tableWidget.setSortingEnabled(True)
            self.tableWidget.setItem(self.rowPosition , 0, QTableWidgetItem(media))
            self.tableWidget.setItem(self.rowPosition , 1, QTableWidgetItem(str(entry))) 
 
    def Install(self):
        try :
            self.dateTime = time.strftime("%d-%m-%Y    %H:%M:%S")
            #==========HOVER ONN TITLE
            rowPosition = self.tableWidget.rowCount()
            index = self.tableWidget.currentRow()
            
            prog = self.tableWidget.item(index,2)
            
            try :
                os.system("EXE\\"+self.actualPath+"\\"+prog.text())
            except:
                pass
            
            query.execute("INSERT into Progs (prog_name,prog_date,prog_state,prog_path) VALUES\
            ('{0}','{1}','{2}','{3}')".format(prog.text(),self.dateTime,"Installed",self.actualPath))
            conn.commit()
            
        except:
            self.processndicator.setText("No folder catégory selected to install")

    def Unzip(self):
        try :
            #==========HOVER ONN TITLE
            rowPosition = self.tableWidget.rowCount()
            index = self.tableWidget.currentRow()
            
            prog = self.tableWidget.item(index,2)
            # with zipfile.ZipFile("EXE\\"+self.actualPath+"\\"+prog.text(), 'r') as zip_ref:
                # zip_ref.extractall("EXE\\Zip")
                # zip.close()
            shutil.unpack_archive("EXE\\"+self.actualPath+"\\"+prog.text(), "EXE\\Zip")
            self.mf.Done()
            
        except:
            self.processndicator.setText("No folder catégory selected to Unzip or folder already satisfied")

    def AddFolder(self):
        try:
            if self.indicator.text() != "My Utilities Manager":
                sender = self.indicator.text()
                dialog = QFileDialog(self)
                dialog.setFileMode(QFileDialog.AnyFile)
                dialog.setViewMode(QFileDialog.Detail)
                
                if dialog.exec_():
                    fileNames = str(dialog.selectedFiles()).strip("['']")
                    if sender == "Developpement" :
                        dst = "EXE\\"+dev
                        shutil.copy(fileNames, dst)
                        self.Menu1()
                        self.processndicator.setText("")
                    elif sender == "Utilities" :
                        dst = "EXE\\"+util
                        shutil.copy(fileNames, dst)
                        self.Menu2()
                        self.processndicator.setText("")
                    elif sender == "Medias" :
                        dst = "EXE\\"+media
                        shutil.copy(fileNames, dst)
                        self.Menu3()
                        self.processndicator.setText("")
            else :
                self.processndicator.setText("No folder catégory selected to copy")
        except:
            self.processndicator.setText("No folder catégory selected")
     
    def DeleteFolder(self):
        try:
            sender = self.indicator.text()
            #==========HOVER ONN TITLE
            rowPosition = self.tableWidget.rowCount()
            index = self.tableWidget.currentRow()
            
            prog = self.tableWidget.item(index,2)
            
            data_file = "EXE\\"+self.actualPath+'\\'+prog.text()
            os.remove(data_file)
            
            if sender == "Developpement" :
                self.Menu1()
            elif sender == "Utilities" :
                self.Menu2()
            elif sender == "Medias" :
                self.Menu3()
        except:
            self.processndicator.setText("No folder catégory selected to delete from")  
            
    def RenameFolder(self):
        try:
            sender = self.indicator.text()
            
            #==========HOVER ONN TITLE
            rowPosition = self.tableWidget.rowCount()
            index = self.tableWidget.currentRow()
            
            self.prog = self.tableWidget.item(index,2)
            self.data_file = "EXE/"+self.actualPath+"/"
            
            self.namer.nameLabel.setText(self.prog.text())
            self.namer.newName.setText(self.prog.text())
            
            self.namer.rename.clicked.connect(self.RenameFolderSlot)
            self.namer.show()
        except:
            self.processndicator.setText("No folder catégory selected to be renamed")
    
    def RenameFolderSlot(self): 
        sender = self.indicator.text()
        if self.namer.newName.text() != "":
            commande = os.rename(self.data_file+self.prog.text(),self.data_file+self.namer.newName.text())
            print(commande)
            self.namer.close()        
        if sender == "Developpement" :
            self.Menu1()
        elif sender == "Utilities" :
            self.Menu2()
        elif sender == "Medias" :
            self.Menu3()
         
if __name__ == '__main__':
    
	app = QApplication(sys.argv)
	ex = Anpr()
    
	sys.exit(app.exec_())