# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'home.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(333, 432)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.Label_2 = QtWidgets.QLabel(self.centralwidget)
        self.Label_2.setObjectName("Label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.Label_2)
        self.DateEdit_2 = QtWidgets.QDateEdit(self.centralwidget)
        self.DateEdit_2.setObjectName("DateEdit_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.DateEdit_2)
        self.Label = QtWidgets.QLabel(self.centralwidget)
        self.Label.setObjectName("Label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.Label)
        self.DateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.DateEdit.setObjectName("DateEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.DateEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "微信小游戏采集"))
        self.Label_2.setText(_translate("MainWindow", "开始"))
        self.Label.setText(_translate("MainWindow", "结束"))
        self.pushButton_2.setText(_translate("MainWindow", "清空"))
        self.pushButton_4.setText(_translate("MainWindow", "跳过"))
        self.pushButton_3.setText(_translate("MainWindow", "同步"))
        self.pushButton.setText(_translate("MainWindow", "开始"))
