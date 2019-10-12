#!/usr/bin/env python3
# coding: utf-8

import csv
import os
import pathlib
import shutil
import smtplib
import sqlite3
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PyQt5.QtCore import Qt, QObject, QDate, pyqtSlot, pyqtSignal, QThreadPool, QRunnable, \
    QDateTime, QRegExp, QSortFilterProxyModel, QSize, QModelIndex
from PyQt5.QtGui import QBrush, QColor, QTextDocument,QPixmap
from PyQt5.QtWidgets import QMainWindow, QStyledItemDelegate, QApplication, QDateEdit, QMessageBox, \
    QDateTimeEdit, QHeaderView, QSpinBox, QFileDialog, QDialog
from docxtpl import DocxTemplate

import TabView2
import moise_alternatif_widgets
import rank_dialogue
import template_dialogue
from DB import *

# TODO: if value error ds calcul total raise error
# TODO: rename pilot_1 to PCB and pilot_2 to PCM
"""
MOISE : MOYEN OPERATIONNEL d'INFORMATION ET DE SOUTIEN DES EQUIPAGES
PROGRAM TO DETECT VALIDITY OF PILOTS FOR SARAA PERIOD
"""


class MainWindow(QMainWindow, moise_alternatif_widgets.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # sshFile = "Style_Gray.qss"
        # with open(sshFile, "r") as fh:
        #     self.setStyleSheet(fh.read())

        imgpth = pathlib.Path.cwd()/'Armee_Air.jpg'
        print(imgpth)
        pix = QPixmap(str(imgpth))
        w = self.Logo_Label.width()
        h = self.Logo_Label.height()
        self.Logo_Label.setPixmap(pix.scaled(w,h))

        # SET UP DB
        self.DB = LmtDataBase()

        # THREAD
        self.threadpool = QThreadPool()

        # SET DB MODEL
        self.db_model = QSqlTableModel()
        self.db_model.setTable('Pilots_exp')
        self.db_model.setEditStrategy(QSqlTableModel.OnFieldChange)

        header_fields = ["PILOTE", "NIA", "CONTRAT", "VSA", "CEMPN", "CTL_TAC",
                         "CTL_CLUB", "SEP", "CONFIDENTIEL_DEF", "LICENSE", "EMAIL", "JOURS RESTANTS"]
        for count, item in enumerate(header_fields, start=1):
            self.db_model.setHeaderData(count, Qt.Horizontal, item)
        self.db_model.select()

        self.tableView.setModel(self.db_model)
        self.tableView.setColumnHidden(0, True)
        self.tableView.resizeColumnsToContents()

        self.insert_combo_pilot_1()
        self.insert_combo_aircraft()
        self.insert_missions()





        # MENU SAVE DB FILE

        self.action_save_file.triggered.connect(self.save_file)


        # BUTTONS ACTIONS
        self.pushButton_add.clicked.connect(self.add_record)
        self.pushButton_remove.clicked.connect(self.delete_row_record)
        # self.pushButton_send_mail.clicked.connect(self.send_email)

        #  LIMITES TAB DELEGATES
        self.custom_delegate = customDelegate()
        for col in range(3, 11):
            self.tableView.setItemDelegateForColumn(col, self.custom_delegate)
        self.meds = self.convert(self.get_date_diff(), self.dictionnaire)

        self.spin_delegate = SpinBoxDelegate()
        self.tableView.setItemDelegateForColumn(12, self.spin_delegate)

        ####################  ui_main_tab  ################################
        self.db_model2 = QSqlRelationalTableModel()
        self.db_model2.setTable('Pilots_hours')
        self.db_model2.setEditStrategy(QSqlRelationalTableModel.OnFieldChange)
        self.db_model2.setRelation(1, QSqlRelation('pilots_id', 'last_name', 'last_name'))
        self.db_model2.setRelation(2, QSqlRelation('pilots_id', 'last_name', 'last_name'))
        self.db_model2.setRelation(3, QSqlRelation('Aircraft', 'immatriculation', 'immatriculation'))
        header_fileds_2 = ["PCB", "PCM", "APPAREIL", "OFF BLOCK", "ON BLOCK", "TOTAL", "MISSION", "COMMENTAIRES"]
        for count, item in enumerate(header_fileds_2, start=1):
            self.db_model2.setHeaderData(count, Qt.Horizontal, item)
        self.db_model2.select()

        # self.tableView_2.setModel(self.db_model2)
        self.tableView_2.setColumnHidden(0, True)
        # self.tableView_2.resizeColumnsToContents()
        # self.tableView_2.horizontalHeader().setStretchLastSection(True)
        self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.custom_delegate2 = customDelegate2()
        self.tableView_2.setItemDelegateForColumn(4, self.custom_delegate2)
        self.tableView_2.setItemDelegateForColumn(5, self.custom_delegate2)

        # self.commbo_delegate = ComboDelegate()
        # self.tableView_2.setItemDelegateForColumn(7,self.commbo_delegate)

        self.dateEdit.setCalendarPopup(True)
        self.dateEdit_2.setCalendarPopup(True)
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit_2.setDate(QDate.currentDate())
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_2.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit.dateTimeChanged.connect(self.dt_changed)
        self.comboBox_price_aircraft.addItems(self.retrieve_aircraft_var())





        # self.label.setText('{} H {} M'.format(*self.hours_minutes()))
        # self.label.setText(str(self.last_col_filtered))
        # self.label.setText('{} H {} M'.format(*self.proxy_hours_minutes()))

        ############  PROXY MODEL ###############
        self.proxyModel2 = MySortFilterProxyModel(self)
        self.proxyModel2.setDynamicSortFilter(True)
        self.proxyModel2.setSourceModel(self.db_model2)

        ###############  2nd proxy on text cascading##################

        self.proxyModel3 = FilterTextProxyModel(self)
        self.proxyModel3.setSourceModel(self.proxyModel2)

        #######################################################

        # self.checkBox_pcm.stateChanged.connect(self.textFilterChanged)

        # self.checkBox_pcm.stateChanged.connect(self.proxyModel2.filterAcceptsRow)

        # for row in range(0,self.proxyModel2.rowCount()):
        #     self.tableView_2.openPersistentEditor(self.proxyModel2.index(row,0))

        # self.proxyView = self.tableView_2
        # self.proxyView.setAlternatingRowColors(True)
        # self.proxyView.setModel(self.proxyModel)
        self.tableView_2.setModel(self.proxyModel2)
        self.tableView_2.verticalHeader().hide()
        self.tableView_2.setAlternatingRowColors(True)
        self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableView_2.setSortingEnabled(True)
        self.tableView_2.sortByColumn(0, Qt.AscendingOrder)

        self.tableView_2.setItemDelegate(RelationalDelegate())
        #
        # self.model_aircraft = QSqlTableModel(self.db_model2)
        # self.delegate_combo = QSqlRelationalDelegate()
        # # self.tableView_2.setModel(self.db_model2)
        # self.tableView_2.setItemDelegate(self.delegate_combo)

        self.lineEdit_search.textChanged.connect(self.textFilterChanged)
        self.lineEdit_search_mission.textChanged.connect(self.textFilterChangesMission)
        self.dateEdit.dateChanged.connect(self.dateFilterChanged)
        self.dateEdit_2.dateChanged.connect(self.dateFilterChanged)

        self.dialogue_ac = Dialogu2()
        self.pushButton_aircraft.clicked.connect(self.show_class_dialogue_aircraft)
        # self.choose_temp = chooseTemplate()
        self.pushButton_termplate_create.setDisabled(True)
        self.pushButton_termplate_create.clicked.connect(self.show_template_dialogue)

        self.pushButton_snapshot_template.clicked.connect(self.write_csv)
        self.pushButton_snapshot_template.clicked.connect(self.btn_clicked_enable)



        self.dialogue_pilot = RankDialogue()
        self.pushButton_add_pilot.clicked.connect(self.show_class_dialogue_pilot)

        self.lineEdit_search.textChanged.connect(self.jaffiche_les_heures)
        self.lineEdit_search_mission.textChanged.connect(self.jaffiche_les_heures)
        self.dateEdit.dateChanged.connect(self.jaffiche_les_heures)
        self.dateEdit_2.dateChanged.connect(self.jaffiche_les_heures)
        self.comboBox_price_aircraft.activated.connect(self.jaffiche_les_heures)

        self.lineEdit_search.textChanged.connect(self.calculate_aircraft_price)
        self.lineEdit_search_mission.textChanged.connect(self.calculate_aircraft_price)
        self.dateEdit.dateChanged.connect(self.calculate_aircraft_price)
        self.dateEdit_2.dateChanged.connect(self.calculate_aircraft_price)
        self.comboBox_price_aircraft.activated.connect(self.calculate_aircraft_price)

    def btn_clicked_enable(self):
        self.pushButton_termplate_create.setDisabled(False)

    def dt_changed(self):
        """on changing dateTimeEdit, dateTimeEdit_2 gets updated accordingly so current DT is minimum selectable"""
        self.dateTimeEdit_2.setMinimumDateTime(self.dateTimeEdit.dateTime())


    def jaffiche_les_heures(self):
        try:
            self.update_record()
            self.label_2.setText('{} H {} M'.format(*self.proxy_hours_minutes()))
        except ValueError as e:
            QMessageBox.critical(self.parent(), "UNE ERREUR DE TYPE VALUEERROR EST SURVENUE ",
                                 f"{e} \nles données de date sont probablement erronées \n"
                                 "Verifier et SUPRIMER l'entrée erroné",
                                 QMessageBox.Ok)
        except UnboundLocalError as d:
            QMessageBox.information(self.parent(), f"ERREUR {d}", "Aucune entrée ne correspond à cette recherche \n",
                                    QMessageBox.Ok)



    def show_class_dialogue_aircraft(self):
        self.dialogue_ac.show()

    def show_class_dialogue_pilot(self):
        self.dialogue_pilot.show()

    def dateFilterChanged(self):
        self.proxyModel2.setFilterMinimumDate(self.dateEdit.date())
        self.proxyModel2.setFilterMaximumDate(self.dateEdit_2.date())

    def textFilterChanged(self):

        if self.checkBox_pcb.isChecked():
            self.tableView_2.setModel(self.proxyModel3)
            self.proxyModel3.set_columns([1])
            caseSensitivity = Qt.CaseInsensitive
            regExp = QRegExp(self.lineEdit_search.text(), caseSensitivity)
            self.proxyModel3.setFilterRegExp(regExp)

        elif self.checkBox_pcm.isChecked():
            self.tableView_2.setModel(self.proxyModel3)
            self.proxyModel3.set_columns([2])
            caseSensitivity = Qt.CaseInsensitive
            regExp = QRegExp(self.lineEdit_search.text(), caseSensitivity)
            self.proxyModel3.setFilterRegExp(regExp)


        else:
            caseSensitivity = Qt.CaseInsensitive
            regExp = QRegExp(self.lineEdit_search.text(), caseSensitivity)
            self.proxyModel2.setFilterRegExp(regExp)

    def textFilterChangesMission(self):
        self.tableView_2.setModel(self.proxyModel3)
        self.proxyModel3.set_columns([7])
        caseSensitivity = Qt.CaseInsensitive
        regExp = QRegExp(self.lineEdit_search_mission.text(), caseSensitivity)
        self.proxyModel3.setFilterRegExp(regExp)

    #################### ALT WIDGETS ##########################################
    def insert_combo_pilot_1(self):
        query = QSqlQuery("SELECT last_name FROM Pilots_id")
        liste = []
        while query.next():
            pilot = query.value(0)
            liste.append(pilot)
        self.comboBox_pilot1.addItems(liste)
        self.comboBox_pilot2.addItems(liste)

    def insert_combo_aircraft(self):
        query = QSqlQuery("SELECT immatriculation FROM Aircraft")
        liste = []
        while query.next():
            aircraft = query.value(0)
            liste.append(aircraft)
        self.comboBox_aircraft.addItems(liste)

    def insert_missions(self):
        '''Links 2 combobox together'''
        self.comboBox_type_msn.addItem('ENTRAINEMENT', ['Navigation', 'Reconnaissance terrain', 'Mania', 'CAS'])
        self.comboBox_type_msn.addItem('PREPARATION OPS', ['Liaison Mise en place sur base', 'Liaison Carburant',
                                                           'Liaison Mécanique', 'Plastron lent Avion',
                                                           'Plastron lent Helico', 'EDSA', 'Contrôle Aérien',
                                                           'Appuie Feu CFAA', 'Au profit de la base Basex',
                                                           'Au profit de la base Photo', 'Au profit de la base Autre'])
        self.comboBox_type_msn.addItem('OPS - CDAOA', ['Banco', 'DPSA', 'PPS', 'Ratest'])
        self.comboBox_type_msn.addItem('RAYONNEMENT BIA', ['Rayonnement BIA'])
        self.comboBox_type_msn.addItem('AUTRE', ['Autre'])

        self.comboBox_type_msn.currentIndexChanged.connect(self.index_changed)
        self.index_changed(self.comboBox_type_msn.currentIndex())

    def index_changed(self, index):
        self.comboBox_ss_type_msn.clear()
        data = self.comboBox_type_msn.itemData(index)
        if data is not None:
            self.comboBox_ss_type_msn.addItems(data)



    ####################END ADD WIDGETS ###################################

    ####################  TEMPLATES WINDOW #########################################

    def show_template_dialogue(self):
        """instantiate template dialogue window in main because we need main variables accessible"""
        # TODO verifier l'import de classe pour pyinstaller

        dialog = QDialog()
        dialog.ui = template_dialogue.Ui_Dialog()
        dialog.ui.setupUi(dialog)
        self.combo = dialog.ui.comboBox
        self.btn_box = dialog.ui.buttonBox

        # self.proxy_pilot_name = self.proxyModel2.index(1, 1).data(Qt.DisplayRole)
        # templates_list = ["template_try.docx", "template_essai.docx"]
        path = pathlib.Path.cwd()
        templates_list2 = [x for x in os.listdir(path) if x.startswith("template") and x.endswith(".docx")]
        dialog.ui.comboBox.addItems(
            templates_list2)  # templates_list2 used: if problem with combo template revert to template_list1
        # self.combo_ac.addItems(self.retrieve_aircraft_var())
        # self.combo_pil.addItems((self.retrieve_pilot_var()))

        self.combo.activated.connect(self.select_template)
        self.btn_box.accepted.connect(self.create_document)
        # self.btn_box.accepted.connect(self.write_csv)
        # self.btn_box.accepted.connect(self.read_stored_pilot)

        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.exec_()

    def select_template(self):
        # print(self.combo.currentText())
        return self.combo.currentText()

    def retrieve_aircraft_var(self):
        """retrieve aircrafts variable from lmtpilots DB and sets it to combobox aircraft price"""
        query_ac = QSqlQuery("SELECT immatriculation FROM Aircraft")
        list_to_be_filled_by_aircraft = []
        while query_ac.next():
            aircraft = query_ac.value(0)
            list_to_be_filled_by_aircraft.append(aircraft)
        return list_to_be_filled_by_aircraft

    def retrieve_pilot_var(self):
        """retrieve pilots var from lmtpilots DB and sets it to combobox"""
        query_pil = QSqlQuery("SELECT last_name FROM Pilots_id")
        list_to_be_filled_by_pilots = []
        while query_pil.next():
            pilot = query_pil.value(0)
            list_to_be_filled_by_pilots.append(pilot)
        return list_to_be_filled_by_pilots

    def calculate_aircraft_price(self):
        # TODO : SET PROPER AIRCRAFT RATE
        try:
            hours = self.proxy_hours_minutes()[0]
            minutes = self.proxy_hours_minutes()[1]
            # rate = 10000
            query = QSqlQuery()
            query.exec_(f'SELECT prix FROM Aircraft WHERE immatriculation = "'
                        f'{self.comboBox_price_aircraft.currentText()}" ')
            while query.next():
                rate = float(query.value(0))
                print(rate)
                print(type(rate))


            # if self.comboBox_price_aircraft.currentText() == "F-GTPH":
            #     rate = 193
            # elif self.comboBox_price_aircraft.currentText() == "F-GJQP":
            #     rate = 85
            # elif self.comboBox_price_aircraft.currentText() == "F-GLPX":
            #     query = QSqlQuery()
            #     query.exec_(f'SELECT prix FROM Aircraft WHERE immatriculation = "'
            #                 f'{self.comboBox_price_aircraft.currentText()}" ')
            #     while query.next():
            #         px = float(query.value(0))
            #         print(px)
            #         print(type(px))

            price = round(hours * rate + (rate * minutes) / 60, 2)
            price_with_int = self.calculate_aircraft_price_with_interest() + price

            # print(price)
            self.label_price.setText(str(price) + " EUROS \n " + str(price_with_int) + " EUROS ")
            return price
        except UnboundLocalError as e:
            print(e)
            pass

    def calculate_aircraft_price_with_interest(self):
        begin = datetime.strptime(self.proxyModel3.index(0, 4).data(Qt.DisplayRole), '%Y/%m/%d %H:%M')
        rows = self.proxyModel3.rowCount() - 1
        end = datetime.strptime(self.proxyModel3.index(rows, 4).data(Qt.DisplayRole), '%Y/%m/%d %H:%M')
        rounded_begin = begin.replace(hour=0, minute=0, second=0, microsecond=0)
        rounded_end = end.replace(hour=0, minute=0, second=0, microsecond=0)
        delta = (rounded_end - rounded_begin).days
        return delta * 34

    def write_csv(self):
        query = QSqlQuery()
        query.exec_(f'SELECT rank,first_name FROM Pilots_id WHERE last_name LIKE "'
                    f'{self.proxyModel3.index(0, 1).data(Qt.DisplayRole)}" ')
        while query.next():
            record = query.record()
            rank = record.value(0)
            first_name = record.value(1)

        vrb_hours = '{} H {} M'.format(*self.proxy_hours_minutes())
        pilots_time_val = [rank, self.proxyModel3.index(0, 1).data(Qt.DisplayRole), first_name, vrb_hours]
        try:

            with open('pilot_time_var.csv', 'a', newline='', ) as f:
                w = csv.writer(f, pilots_time_val)
                w.writerow(pilots_time_val)
        except IOError as e:
            QMessageBox.critical(self.parent(), "ERREUR", f"Erreur de type {e}")
        finally:
            QMessageBox.information(self.parent(), "SUCCES", f"LA LIGNE {pilots_time_val} A BIEN ETE INSERER")

    # def read_stored_pilot(self):
    #     my_list = []
    #     try:
    #         with open('pilot_time_var.csv', newline='') as f:
    #             r = csv.reader(f)
    #             for row in r:
    #                 my_list.append(row)
    #         return my_list
    #     except IOError as e:
    #         QMessageBox.critical((self.parent(), "ERREUR", f" ERREUR de type {e}"))



    def create_document(self):

        current_date = time.strftime('%d/%m/%Y', time.localtime())
        vrb_hours = '{} H {} M'.format(*self.proxy_hours_minutes())
        proxy_pilot_name = self.proxyModel2.index(0, 1).data(Qt.DisplayRole)
        proxy_mission_type = self.proxyModel3.index(0, 7).data(Qt.DisplayRole)
        # fichier = self.read_stored_pilot()
        # print(fichier)
        try:
            data = ReadCsvFile("pilot_time_var.csv")
        except FileNotFoundError as e:
            Creation = QMessageBox.critical(self.parent(), "PAS DE FICHIER",
                                            "Voulez vous en creer un ?",
                                            QMessageBox.Yes, QMessageBox.No)
            if Creation == QMessageBox.Yes:
                with open('pilot_time_var.csv', 'a', newline='', ) as f:
                    w = csv.writer(f, delimiter=',')
                    w.writerow(['DUMMY', 'DUMY', 'DUMMY', '24 H 00 M'])

        # print(data.get_row())
        # try:
        clean_row = data.clean_row()
        get_hour = data.get_hour()

        # except UnboundLocalError as e:
        #     print(e)

        # pilot1 = str(data.get_row()).replace(",","").replace("'","")
        # print(pilot1)

        # my_string = ', '.join(pilot1)
        # print(type(pilot1))
        # print(pilot1)


        displayed_hours = self.label_2.text()

        # print(vrb_hours, vrb_aircraft, vrb_pilots, proxy_pilot_name,displayed_hours)
        #
        doc = DocxTemplate(self.select_template())
        # print('the text is :'+self.select_template())
        # context = {'company_name': "World company", 'my_name': "Capitaine Morgand", 'hours': vrb_hours}
        if self.select_template() == 'template_try.docx':
            context = {'company_name': "World company", 'my_name': "Capitaine Morgand", 'hours': vrb_hours,
                       'clean_row': clean_row, 'get_hour': get_hour}
        elif self.select_template() == 'template_CR.docx':
            context = {'current_date': current_date, f'{proxy_mission_type}': proxy_mission_type, 'hours': vrb_hours}
            # context = {'current_date': current_date, 'Avion': proxy_mission_type}
        else:
            context = {'company_name': "My company", f'{proxy_mission_type}': proxy_mission_type, 'hours': vrb_hours}
        # try:
        doc.render(context)
        doc.save("Generated_" + self.select_template())
        # finally:
        #     with open('pilot_time_var.csv', 'w', newline='', ) as f:
        #         w = csv.writer(f)





    ########################   END TEMPLATES WINDOW    ############################3


    def save_file(self):
        '''Saves cwd DB to chosen directory i.e file_name[0] in .db format'''
        file_name = QFileDialog.getSaveFileName(self, 'Sauvegarder BDD', '', 'SQL Files(*.db)', '')
        if file_name[0] is not None and file_name[0] != '':
            try:
                shutil.copy2(str(pathlib.Path.cwd().joinpath('LmtPilots.db')), file_name[0])
                # shutil.copy2(pathlib.Path.cwd() / 'LmtPilots.db', file_name[0])
            except Exception as e:
                QMessageBox.Abort('pas de fichier selectionné erreur {}'.format(e))


    def oh_no(self):
        """start email thread"""
        worker = Worker(self.send_email)
        self.threadpool.start(worker)

    @pyqtSlot()
    def on_pushButton_send_mail_clicked(self):
        confirm_sending = "Voulez vous vraiment envoyer les notifications ? "
        reply = QMessageBox.question(self, 'message', confirm_sending, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.oh_no()
        else:
            QMessageBox.Cancel

    def add_record(self):
        '''add row on FIRST TABLE'''
        row = self.db_model.rowCount()
        self.db_model.insertRow(row)

    def delete_row_record(self):
        '''remove row on FIRST TABLE'''
        deleteconfirmation = QMessageBox.critical(self.parent(), "Delete row",
                                                  "Voulez vous vraiment supprimer l'entrée ?",
                                                  QMessageBox.Yes, QMessageBox.No)
        if deleteconfirmation == QMessageBox.Yes:
            model = self.db_model
            indices = self.tableView.selectionModel().selectedRows()
            for index in sorted(indices):
                model.removeRow(index.row())
            self.db_model.select()

    ##################     MAIL  ######################
    def get_date_diff(self):
        query = QSqlQuery(
            "SELECT pilot_1,nia_pilot,contrat_reserve, vsa, cempn, ctl_tactique, "
            "ctl_aeroclub, sep, habilitation_cd,licence,pilot_mail FROM Pilots_exp")

        rec = query.record()
        cols = [rec.indexOf(name) for name in ("contrat_reserve", "vsa", "cempn", "ctl_tactique",
                                               "ctl_aeroclub", "sep", "habilitation_cd", "licence")]
        results = []
        while query.next():
            pilot_1 = query.value(rec.indexOf("pilot_1"))
            pilot_mail = query.value(rec.indexOf("pilot_mail"))
            dates = [QDate.fromString(query.value(col), "yyyy/MM/dd") for col in cols]
            filter_columns = [col for col, date in zip(cols, dates) if date < QDate.currentDate()]
            if filter_columns:
                v = [pilot_1, filter_columns, pilot_mail]
                results.append(v)
        # print(v)
        return results

    dictionnaire = {2: "CONTRAT", 3: "VSA", 4: "CEMPN", 5: "CONTROL TAC", 6: "CONTROL CLUB",
                    7: "SEP", 8: "CONTFIDENTIEL DEFENCE", 9: "LICENCE"}

    # diff way : dico = {k:v for (k,v) in enumerate(une_liste,start=1)}

    def convert(self, l, d):
        """Replaces values in nested list with dictionnary values:
        If item on my list is a list then recurse, otherwise use dict.get with default parameter to convert the item
        my_list = ['a','b','c','dog', ['pig','cat'], 'd']
        my_dict = {'dog':'c','pig':'a','cat':'d'}
        def convert(l, d):
            return [convert(x, d) if isinstance(x, list) else d.get(x, x) for x in l]
        print(convert(my_list, my_dict))
        Output:
        ['a', 'b', 'c', 'c', ['a', 'd'], 'd']
"""
        return [self.convert(x, d) if isinstance(x, list) else d.get(x, x) for x in l]

    def send_email(self, progress_callback):
        print("marche mon vieux")
        try:
            for i in range(len(self.meds)):
                email = '< {}'.format(self.meds[i][2]) + ' >'
                name = ' {}'.format(self.meds[i][0])
                renewal = ' {}'.format(','.join(self.meds[i][1]))
                print(email)
                print(name)
                print(renewal)
                msg = MIMEMultipart()
                msg['from'] = os.environ.get("LUIGI_MAIL")
                msg['to'] = email
                # msg['to'] = "{}".format(self.get_date_diff())
                password = os.environ.get('LUIGI_PWD')
                msg['subject'] = "test subject"
                body = "<h1> Bonjour {} vous devez renouveler " \
                       "les éléments suivants: {} </h1><h2>Merci de renvoyer la mise à jour à l'adresse ci-dessous</h2>" \
                       "<p> m.morgand@gmail.com</p>".format(name, renewal)
                print(body)
                msg.attach(MIMEText(body, 'html'))
                print(msg)
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.ehlo()
                server.starttls()
                server.login(msg['from'], password)
                # message = 'Subject: {}\n\n{}'.format(subject, msg)
                server.sendmail(msg['from'], msg['to'], msg.as_string())
                server.quit()
                print("Success: Email sent!")
        except Exception as e:
            print(e, file=sys.stderr)

        ################### END MAIL ##########################

        ################### ui_main_tab2 #########################
    #########   FILTER ROW  ##########
    # def get_filtered_rows(self):
    #     print("rows in fitered view is {} ".format(self.proxyModel2.rowCount()))
    #     print("rows in original model is {}".format(self.db_model2.rowCount()))

    def last_col_filtered(self):
        """Gets all the data from the filtered model and returns last column i.e total hours """
        data = []
        for row in range(self.proxyModel3.rowCount()):
            data.append([])
            for column in range(self.proxyModel3.columnCount()):
                index = self.proxyModel3.index(row, column)
                data[row].append(str(self.proxyModel3.data(index)))
            data2 = [col[6] for col in data]
        # print(data)
        # print(data2)
        return data2

    def convert_last_col_filtered(self):
        # TODO: fix problem on value error when new line without time
        try:
            date = [datetime.strptime(x, "%H:%M:%S") for x in self.last_col_filtered()]
            liste1 = []
            for i in date:
                dt = timedelta(hours=i.hour, minutes=i.minute, seconds=i.second)
                liste1.append(dt)
            return (sum(liste1, timedelta()))
        except ValueError:
            self.update_record()

    def proxy_hours_minutes(self):
        """conversion of time delta get_tot_hours to hours"""

        td = self.convert_last_col_filtered()
        resultat = td.days * 24 + td.seconds // 3600, (td.seconds // 60) % 60
        # print('{} H {} M'.format(*resultat))
        print(resultat)
        return resultat

    # def update_combobox_pilots(self):
    #     # Filling combox _avion
    #     query_aircraft = QSqlQuery("SELECT immatriculation FROM Aircraft")
    #     liste_ac = []
    #     while query_aircraft.next():
    #         aircraft = query_aircraft.value(0)
    #         liste_ac.append(aircraft)
    #     # self.comboBox_avion.addItems(liste_ac)
    #     # self.comboBox_sel_ac.addItems(liste_ac)
    #     return liste_ac
    #
    # def get_tot_hours(self):
    #     """select dates from database """
    #     query1 = QSqlQuery("SELECT date_time1,date_time2 FROM Pilots_hours")
    #     liste = []
    #     while query1.next():
    #         date1 = query1.value(0)
    #         date2 = query1.value(1)
    #         essai = datetime.strptime(date2, "%Y/%m/%d %H:%M") - datetime.strptime(date1, "%Y/%m/%d %H:%M")
    #         liste.append(essai)
    #     total = sum(liste, timedelta())
    #     return total
    #
    # def hours_minutes(self):
    #     """conversion of time delta get_tot_hours to hours"""
    #     td = self.get_tot_hours()
    #     # td = self.convert_last_col_filtered()
    #     resultat = td.days * 24 + td.seconds // 3600, (td.seconds // 60) % 60
    #     print('{} H {} M'.format(*resultat))
    #     return resultat

    def get_hours_diff(self):
        '''used by update_record method to enter total column in SQL'''
        query1 = QSqlQuery("SELECT date_time1,date_time2 FROM Pilots_hours")
        result = []
        while query1.next():
            date1 = query1.value(0)
            date2 = query1.value(1)
            try:
                diff = datetime.strptime(date2, "%Y/%m/%d %H:%M") - datetime.strptime(date1, "%Y/%m/%d %H:%M")
            except ValueError as e:
                msg = QMessageBox()
                msg.critical(self, "ATTENTION", "Vous n\'avez pas entré d'heure dans les cases prevues ")
                print(f'erreur de type {e} : contacter le developeur')
            result.append(str(diff))
        return result

    # @pyqtSlot()
    # def on_pushButton_clicked(self):
    #     #     self.add_record2()
    #     #
    #     # def add_record2(self):
    #     row = self.proxyModel2.rowCount()
    #     self.db_model2.insertRow(row)

    @pyqtSlot()
    def on_pushButton_insert_clicked(self):
        query = QSqlQuery()
        query.prepare(
            "INSERT INTO Pilots_hours (pilot_1,pilot_2, aircraft, date_time1 , date_time2, mission, commentaires )"  "VALUES (?,?,?,?,?,?,?)")
        query.bindValue(0, self.comboBox_pilot1.currentText())
        query.bindValue(1, self.comboBox_pilot2.currentText())
        query.bindValue(2, self.comboBox_aircraft.currentText())
        query.bindValue(3, self.dateTimeEdit.text())
        query.bindValue(4, self.dateTimeEdit_2.text())
        query.bindValue(5, self.comboBox_ss_type_msn.currentText())
        query.bindValue(6, self.lineEdit_commentaires.text())
        query.exec_()
        self.db_model2.select()
        msg = QMessageBox()
        msg.setText("Données inserées dans la base de données")
        msg.exec_()

    @pyqtSlot()
    def on_rmv_btn_clicked(self):
        self.remove_row()

    def remove_row(self):
        deleteconfirm = QMessageBox.critical(self.parent(), "SUPRIMMER LE RANG", "SUPRIMMER LE RANG", QMessageBox.Yes,
                                             QMessageBox.No)
        if deleteconfirm == QMessageBox.Yes:
            position = self.tableView_2.currentIndex().row()
            self.proxyModel3.removeRow(position, 1)
            # TO REMOVE DIRECTLY FROM DB MODEL BUT DOESN'T WORK IF PROXY IN BETWEEN
            # index = self.tableView_2.selectionModel().currentIndex()
            # self.db_model2.removeRow(index)
            # self.db_model2.submitAll()
            # self.db_model2.select()
            return
        else:
            # index = self.tableView_2.selectionModel().currentIndex().row()
            # print(index)
            return
        #
        # ligne = self.tableView_2.selectionMode().currentIndex().row()
        # print(ligne)
        # self.proxyModel2.removeRow(ligne)

    def update_record(self):
        """UPDATES EACH SQL ROW WITH TIME DELTA FROM PREVIOUS 2 COLUMNS"""
        # print(self.get_hours_diff())
        conn = sqlite3.connect("LmtPilots.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Pilots_hours")
        rowids = [row[0] for row in cur.execute('SELECT rowid FROM Pilots_hours')]
        cur.executemany('UPDATE Pilots_hours SET total=? WHERE id=?', zip(self.get_hours_diff(), rowids))
        conn.commit()
        self.db_model2.select()
        # print(self.get_tot_hours())


    #############  count days #####################
    def count_days(self):
        query = QSqlQuery("SELECT pilot_1,date_time1 FROM Pilots_hours")
        dcn = []
        date_1 = []
        while query.next():
            pilot = query.value(0)
            date = query.value(1)
            dcn.append(pilot)
            # date_1.append(date)
            date_1.append(datetime.strptime(date, "%Y/%m/%d %H:%M").date())
        grouped_list = zip(dcn,date_1)
        grouped_list = list(grouped_list)
        set_grouped_list = Counter(set(grouped_list))

        dict_counter = Counter(x for x, y in set(set_grouped_list))

        for i in dict_counter.items():
            k = i[0]
            k2 = i[1]
            query2 = QSqlQuery("UPDATE Pilots_exp SET jours_restants =+ {} WHERE pilot_1 LIKE '{}'".format(k2,k))
            query2.exec_()

    @pyqtSlot()
    # TODO: Automate method and remove button
    def on_pushButton_update_clicked(self):
        self.count_days()

    ############ end count days ################

    # @pyqtSlot()
    # def on_pushButton_update_clicked(self):
    #     self.update_record()
    # self.calculate_aircraft_price()
    # self.calculate_aircraft_price_with_interest()
    # try:
    #     self.label_2.setText('{} H {} M'.format(*self.proxy_hours_minutes()))
    # except ValueError as e:
    #     QMessageBox.critical(self.parent(), "UNE ERREUR DE TYPE VALUEERROR EST SURVENUE ",
    #                          f"{e} \nles données de date sont probablement erronées \n"
    #                          "Verifier et SUPRIMER l'entrée erroné",
    #                          QMessageBox.Ok)


class ReadCsvFile():
    def __init__(self, filename):
        with open(filename, "r") as f_input:
            csv_input = csv.reader(f_input)
            self.details = list(csv_input)

    def get_row(self):
        return self.details

    def get_hour(self):
        h = [el[3] for el in self.get_row()]
        return h

    def clean_row(self):
        o = [el[:-1] for el in self.get_row()]
        m = [[' '.join(i)] for i in o]

        return m
        # the_lines = []
        # for i in m:
        #     for j in i:
        #         the_lines.append(j)
        #
        # return the_lines

        #
        # return j






class customDelegate2(QStyledItemDelegate):
    """DELEGATE INSERT CUSTOM DATEEDIT IN CELL """

    def __init__(self, parent=None):
        super(customDelegate2, self).__init__(parent)

    def createEditor(self, parent, option, index):
        date_edit = QDateTimeEdit(parent)
        date_edit.setDisplayFormat("yyyy/MM/dd HH:mm")
        date_edit.setDateTime(QDateTime.currentDateTime())

        date_edit.setCalendarPopup(True)
        return date_edit

    def setModelData(self, editor, model, index):
        value = editor.dateTime().toString("yyyy/MM/dd HH:mm")
        model.setData(index, value)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        qdate = QDateTime().fromString(value, "yyyy/MM/dd HH:mm")
        editor.setDateTime(qdate)


class MySortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(MySortFilterProxyModel, self).__init__(parent)

        self.minDate = QDate()
        self.maxDate = QDate()

    def setFilterMinimumDate(self, date):
        self.minDate = date
        self.invalidateFilter()

    def filterMinimumDate(self):
        return self.minDate

    def setFilterMaximumDate(self, date):
        self.maxDate = date
        self.invalidateFilter()

    def filterMaximumDate(self):
        return self.maxDate

    def filterAcceptsRow(self, sourceRow, sourceParent):

        index0 = self.sourceModel().index(sourceRow, 1, sourceParent)
        index1 = self.sourceModel().index(sourceRow, 2, sourceParent)
        index2 = self.sourceModel().index(sourceRow, 3, sourceParent)
        index3 = self.sourceModel().index(sourceRow, 4, sourceParent)

        return ((self.filterRegExp().indexIn(self.sourceModel().data(index0)) >= 0
                 or self.filterRegExp().indexIn(self.sourceModel().data(index1)) >= 0
                 or self.filterRegExp().indexIn(self.sourceModel().data(index2)) >= 0)
                and self.dateInRange(self.sourceModel().data(index3)))

    def dateInRange(self, date):
        try:
            date = datetime.strptime(date, "%Y/%m/%d %H:%M")
        except ValueError:
            pass
        except TypeError:
            pass

        return ((not self.minDate.isValid() or date >= self.minDate)
                and (not self.maxDate.isValid() or date <= self.maxDate))


class FilterTextProxyModel(QSortFilterProxyModel):
    """Class taken from stack Eyllanesc to filter text on columns desired and not all of them"""

    def __init__(self, parent=None):
        super(FilterTextProxyModel, self).__init__(parent)
        self._columns = []

    def set_columns(self, columns):
        self._columns = columns
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if not self._columns:
            return True
        values = []
        for c in range(self.sourceModel().columnCount()):
            if c in self._columns:
                ix = self.sourceModel().index(sourceRow, c, sourceParent)
                values.append(self.filterRegExp().indexIn(ix.data()) >= 0)
        return any(values)

    def removeRow(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(int(rows)):
            self.sourceModel().removeRow(position)
        self.endRemoveRows()



################### END ui_main_tab2 #######################

class customDelegate(QStyledItemDelegate):
    """DELEGATE INSERT CUSTOM DATEEDIT IN CELL + COLOR CELLS(RED OR YELLOW) DEPENDING ON DATE WITH InitStyleOption"""

    def __init__(self, parent=None):
        super(customDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        date_edit = QDateEdit(parent)
        date_edit.setDisplayFormat("yyyy/MM/dd")
        date_edit.setDate(QDate.currentDate())

        date_edit.setCalendarPopup(True)
        return date_edit

    def setModelData(self, editor, model, index):
        value = editor.date().toString("yyyy/MM/dd")
        model.setData(index, value)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        qdate = QDate().fromString(value, "yyyy/MM/dd")
        editor.setDate(qdate)

    # class DateDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(customDelegate, self).initStyleOption(option, index)
        t = QDate.fromString(index.data(), "yyyy/MM/dd")
        if t < QDate.currentDate():
            option.backgroundBrush = QBrush(QColor("red"))
        elif not t > QDate.currentDate().addDays(60):
            option.backgroundBrush = QBrush(QColor("yellow"))
        # TODO : Review text to be set to blue


class SpinBoxDelegate(QStyledItemDelegate):
    """Spinbox for days in reserve days left on 1st tableview"""

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(0)
        editor.setMaximum(40)

        return editor

    def setEditorData(self, spinBox, index):
        value = index.model().data(index, Qt.EditRole)
        spinBox.setValue(value)

    def setModelData(self, spinBox, model, index):
        spinBox.interpretText()
        value = spinBox.value()

        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


#
# class ComboDelegate(QStyledItemDelegate):
#     """
#     A delegate that places a fully functioning QComboBox in every
#     cell of the column to which it's applied
#     """
#
#     def __init__(self, parent=None):
#         super(QStyledItemDelegate, self).__init__(parent)
#
#     def createEditor(self, parent, option, index):
#         combo = QComboBox(parent)
#         li = []
#         li.append("Zero")
#         li.append("One")
#         li.append("Two")
#         li.append("Three")
#         li.append("Four")
#         li.append("Five")
#         combo.addItems(li)
#         # self.connect(combo, QtCore.SIGNAL("currentIndexChanged(int)"), self, QtCore.SLOT("currentIndexChanged()"))
#         combo.currentIndexChanged.connect(self.currentIndexChanged)
#         return combo
#
#     def setEditorData(self, editor, index):
#         editor.blockSignals(True)
#
#
#         editor.setCurrentIndex(index.row())
#         editor.blockSignals(False)
#
#     def setModelData(self, editor, model, index):
#         model.setData(index, editor.currentIndex())
#
#     @pyqtSlot()
#     def currentIndexChanged(self):
#         self.commitData.emit(self.sender())


class RelationalDelegate(QSqlRelationalDelegate):
    """
    Delegate handles custom editing. This allows the user to have good
    editing experience.

    Because the join table uses a proxy model a subclass QSqlRelationalDelegate
    is required. This is to support the foreign key combobox.
    """

    def __init__(self, parent=None):
        """
        Class constructor.
        """
        # Python super lets you avoid referring to the base class explicitly.
        super(RelationalDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        """
        This creates the editors in the delegate.
        Reimplemented from QAbstractItemDelegate::createEditor().
        Returns the widget used to edit the item specified by
        index for editing.

        The parent widget and style option are used to control how the
        editor widget appears.

        1. Get the model associated with the view. In this case it is the
            QSortFilterProxyModel.

        2. Because with a proxy model the views index does not have to be the
        same as the models index. If one sorts,
        then the index are not the same.

        3. mapToSource.
            This is why mapToSource is being used.
            mapToSouce Reimplement this function to return the
            model index in the proxy model that corresponds to the
            sourceIndex from the source model.

        4. Return the createEditor with the base index being set to the source
            model and not the proxy model.
        """
        if index.column() == 1 or 2 or 3:
            proxy = index.model()
            base_index = proxy.mapToSource(index)
            return super(RelationalDelegate, self).createEditor(parent, option, base_index)
        else:
            return super(RelationalDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """
        Once the editor has been created and given to the view
        the view calls setEditorData().
        This gives the delegate the opportunity to populate the editor
        with the current data, ready for the user to edit.

        Sets the contents of the given editor to the data for the item
        at the given index.

        Note that the index contains information about the model being used.

        The base implementation does nothing.
        If you want custom editing you will need to reimplement this function.

        1. Get the model which is a QSortFilterProxyModel.

        2. Call mapToSource().
        Because with a proxy model the views index does not have to be the
        same as the models index. If one sorts,
        then the index are not the same.
        This is why mapToSource is being used. MapToSouce Reimplement this
        function to return the model index in the proxy model
        that corresponds to the sourceIndex from the source model.

        3. Return setEditorData with the editor and the mapToSource index.

        4. Else for all other columns return the base method.
        """

        if index.column() == 1 or 2 or 3:
            proxy = index.model()
            base_index = proxy.mapToSource(index)
            return super(RelationalDelegate, self).setEditorData(editor, base_index)
        else:
            return super(RelationalDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 1 or 2 or 3:
            base_model = model.sourceModel()
            base_index = model.mapToSource(index)
            return super(RelationalDelegate, self).setModelData(editor, base_model, base_index)
        else:
            super(RelationalDelegate, self).setModelData(editor, model, index)

    def sizeHint(self, option, index):
        """
        This pure abstract function must be reimplemented if you want to
        provide custom rendering. The options are specified by option and
        the model item by index.

        """
        if index.isValid():
            column = index.column()
            text = index.model().data(index)
            document = QTextDocument()
            document.setDefaultFont(option.font)
            # change cell Width, height (One can add or subtract to change the relative dimension)
            return QSize(QSqlRelationalDelegate.sizeHint(self, option, index).width() - 200,
                         QSqlRelationalDelegate.sizeHint(self, option, index).height() + 40)
        else:
            return super(RelationalDelegate, self).sizeHint(option, index)


class Dialogu2(QDialog, TabView2.Ui_insertDialogu):
    """Opens Dialogue box to insert New Aircraft in database"""

    def __init__(self, parent=None):
        super(Dialogu2, self).__init__(parent)
        self.setupUi(self)
        self.buttonBox.clicked.connect(self.setdata_aircraft)

    def setdata_aircraft(self):
        query = QSqlQuery()
        query.prepare("INSERT INTO Aircraft(immatriculation,type_ac,puissance,prix)" "VALUES(?,?,?,?)")
        query.bindValue(0, self.lineEdit.text())
        query.bindValue(1, self.lineEdit_2.text())
        query.bindValue(2, self.lineEdit_3.text())
        query.bindValue(3,self.lineEdit_prix_avion.text())
        query.exec_()
        msg = QMessageBox()
        msg.setText("Aéronef inseré dans la base de données")
        msg.exec_()


class RankDialogue(QDialog, rank_dialogue.Ui_Dialog):
    def __init__(self, parent=None):
        super(RankDialogue, self).__init__(parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.insert_pilot_in_db)
        self.buttonBox.rejected.connect(self.reject)

        ranks = ["AVIATEUR", "1ere CLASSE", "CAPORAL", "CAPORAL CHEF",
                 "SERGENT", "SERGENT-CHEF",
                 "ADJUDANT", "ADJUDANT CHEF", "MAJOR",
                 "ASPIRANT", "SOUS LIEUTENANT", "LIEUTENANT", "CAPITAINE",
                 "COMMANDANT", "LEUTENANT COLONEL", "COLONEL"]
        self.comboBox_rank.addItems(ranks)

    def insert_pilot_in_db(self):
        query = QSqlQuery()
        query.prepare("INSERT INTO Pilots_id(rank,first_name,last_name,nia)" "VALUES(?,?,?,?)")
        query.bindValue(0, self.comboBox_rank.currentText())
        query.bindValue(1, self.lineEdit_prenom.text())
        query.bindValue(2, self.lineEdit_nom.text())
        query.bindValue(3, self.lineEdit_nia.text())
        query.exec_()
        msg = QMessageBox()
        msg.setText("Pilote inseré dans la base de données")
        msg.exec_()







# class chooseTemplate(QDialog, template_dialogue.Ui_Dialog):
#     """Opens Dialogue box to choose docx templates"""
#
#     def __init__(self, parent=None):
#         super(chooseTemplate, self).__init__(parent)
#         self.setupUi(self)
#
#         templates_list = ["template_try.docx","template_essai.docx"]
#         self.comboBox.addItems(templates_list)
#
#         self.comboBox.activated.connect(self.select_template)
#         self.buttonBox.accepted.connect(self.create_docx_document)
#
#
#     def create_docx_document(self):
#         print("it is alive, alive")
#         connectClass = MainWindow.set_templates_fixes(self)
#         # connectClass2 = MainWindow.proxy_hours_minutes(self)
#         # print(MainWindow.label_2())
#
#
#
#
#     def select_template(self):
#         print(self.comboBox.currentText())
#         return self.comboBox.currentText()


# def create_templates(self):
#
#     tpm = template_work.docxTemplateCreation()
#     tpm.create_docx_document("template_try.docx")



############ CLASS THREADING #############
class WorkerSignal(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignal()

        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        form = MainWindow()
        # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        form.show()
        app.exec_()
        sys.exit(0)
    except NameError:
        print("Name Error: ", sys.exc_info()[1])
    except SystemExit:
        print("Closing Window....")
    except Exception:
        print(sys.exc_info()[1])
