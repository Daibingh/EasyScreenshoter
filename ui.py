# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(748, 210)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout.addWidget(self.comboBox)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout.addWidget(self.lineEdit_3)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setStyleSheet("")
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_link1 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_link1.setObjectName("lineEdit_link1")
        self.gridLayout.addWidget(self.lineEdit_link1, 0, 0, 1, 1)
        self.pushButton_copy1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_copy1.setObjectName("pushButton_copy1")
        self.gridLayout.addWidget(self.pushButton_copy1, 0, 1, 1, 1)
        self.lineEdit_link2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_link2.setObjectName("lineEdit_link2")
        self.gridLayout.addWidget(self.lineEdit_link2, 1, 0, 1, 1)
        self.pushButton_copy2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_copy2.setObjectName("pushButton_copy2")
        self.gridLayout.addWidget(self.pushButton_copy2, 1, 1, 1, 1)
        self.lineEdit_link3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_link3.setObjectName("lineEdit_link3")
        self.gridLayout.addWidget(self.lineEdit_link3, 2, 0, 1, 1)
        self.pushButton_copy3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_copy3.setObjectName("pushButton_copy3")
        self.gridLayout.addWidget(self.pushButton_copy3, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 748, 26))
        self.menubar.setObjectName("menubar")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionremote = QtWidgets.QAction(MainWindow)
        self.actionremote.setCheckable(True)
        self.actionremote.setChecked(True)
        self.actionremote.setObjectName("actionremote")
        self.actionlogin = QtWidgets.QAction(MainWindow)
        self.actionlogin.setCheckable(False)
        self.actionlogin.setChecked(False)
        self.actionlogin.setObjectName("actionlogin")
        self.actionremote_2 = QtWidgets.QAction(MainWindow)
        self.actionremote_2.setObjectName("actionremote_2")
        self.actionimages = QtWidgets.QAction(MainWindow)
        self.actionimages.setObjectName("actionimages")
        self.menuSettings.addAction(self.actionremote)
        self.menuSettings.addAction(self.actionlogin)
        self.menuView.addAction(self.actionimages)
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "截图"))
        self.comboBox.setItemText(0, _translate("MainWindow", "full"))
        self.comboBox.setItemText(1, _translate("MainWindow", "-1"))
        self.comboBox.setItemText(2, _translate("MainWindow", "-2"))
        self.label_3.setText(_translate("MainWindow", "Q:"))
        self.lineEdit_3.setText(_translate("MainWindow", "100"))
        self.label_2.setText(_translate("MainWindow", "path:"))
        self.label.setText(_translate("MainWindow", "prefix:"))
        self.label_4.setText(_translate("MainWindow", "Apply for a token"))
        self.pushButton_copy1.setText(_translate("MainWindow", "copy"))
        self.pushButton_copy2.setText(_translate("MainWindow", "copy"))
        self.pushButton_copy3.setText(_translate("MainWindow", "copy"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.actionremote.setText(_translate("MainWindow", "remote"))
        self.actionlogin.setText(_translate("MainWindow", "login"))
        self.actionremote_2.setText(_translate("MainWindow", "remote"))
        self.actionimages.setText(_translate("MainWindow", "images"))

