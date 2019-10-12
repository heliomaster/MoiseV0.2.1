# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rank_dialogue.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(340, 203)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 118, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_grade = QtWidgets.QLabel(Dialog)
        self.label_grade.setAlignment(QtCore.Qt.AlignCenter)
        self.label_grade.setObjectName("label_grade")
        self.verticalLayout.addWidget(self.label_grade)
        self.comboBox_rank = QtWidgets.QComboBox(Dialog)
        self.comboBox_rank.setObjectName("comboBox_rank")
        self.verticalLayout.addWidget(self.comboBox_rank)
        self.label_prenom = QtWidgets.QLabel(Dialog)
        self.label_prenom.setAlignment(QtCore.Qt.AlignCenter)
        self.label_prenom.setObjectName("label_prenom")
        self.verticalLayout.addWidget(self.label_prenom)
        self.lineEdit_prenom = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_prenom.setObjectName("lineEdit_prenom")
        self.verticalLayout.addWidget(self.lineEdit_prenom)
        self.label_nom = QtWidgets.QLabel(Dialog)
        self.label_nom.setAlignment(QtCore.Qt.AlignCenter)
        self.label_nom.setObjectName("label_nom")
        self.verticalLayout.addWidget(self.label_nom)
        self.lineEdit_nom = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_nom.setObjectName("lineEdit_nom")
        self.verticalLayout.addWidget(self.lineEdit_nom)
        self.label_nia = QtWidgets.QLabel(Dialog)
        self.label_nia.setAlignment(QtCore.Qt.AlignCenter)
        self.label_nia.setObjectName("label_nia")
        self.verticalLayout.addWidget(self.label_nia)
        self.lineEdit_nia = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_nia.setObjectName("lineEdit_nia")
        self.verticalLayout.addWidget(self.lineEdit_nia)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 2, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.label_grade.setBuddy(self.comboBox_rank)
        self.label_prenom.setBuddy(self.lineEdit_prenom)
        self.label_nom.setBuddy(self.lineEdit_nom)
        self.label_nia.setBuddy(self.lineEdit_nia)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Entrer Nouveau Pilote"))
        self.label_grade.setText(_translate("Dialog", "GRADE"))
        self.label_prenom.setText(_translate("Dialog", "PRENOM"))
        self.label_nom.setText(_translate("Dialog", "NOM"))
        self.label_nia.setText(_translate("Dialog", "NIA"))

