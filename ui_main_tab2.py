import sqlite3
import sys
from datetime import datetime, timedelta

from PyQt5.QtCore import pyqtSlot, QDateTime, QDate, QRegExp, QSortFilterProxyModel, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyledItemDelegate, QDateTimeEdit, QHeaderView

import moise
from DB import *


class MainWindow2(QMainWindow, moise.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow2, self).__init__(parent)
        self.setupUi(self)
        self.DB = LmtDataBase()
        self.db_model2 = QSqlRelationalTableModel()
        self.db_model2.setTable('Pilots_hours')
        self.db_model2.setEditStrategy(QSqlRelationalTableModel.OnFieldChange)
        self.db_model2.setRelation(2, QSqlRelation('Aircraft', 'immatriculation', 'immatriculation'))
        self.db_model2.select()
        # self.tableView_2.setModel(self.db_model2)
        self.tableView_2.setColumnHidden(0, True)
        # self.tableView_2.resizeColumnsToContents()
        # self.tableView_2.horizontalHeader().setStretchLastSection(True)
        self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.custom_delegate2 = customDelegate2()
        self.tableView_2.setItemDelegateForColumn(3, self.custom_delegate2)
        self.tableView_2.setItemDelegateForColumn(4, self.custom_delegate2)

        self.dateEdit.setCalendarPopup(True)
        self.dateEdit_2.setCalendarPopup(True)
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit_2.setDate(QDate.currentDate())

        # self.label.setText('{} H {} M'.format(*self.hours_minutes()))
        # self.label.setText(str(self.last_col_filtered))
        # self.label.setText('{} H {} M'.format(*self.proxy_hours_minutes()))

        ############  PROXY MODEL ###############
        self.proxyModel2 = MySortFilterProxyModel2(self)
        self.proxyModel2.setDynamicSortFilter(True)
        self.proxyModel2.setSourceModel(self.db_model2)

        # self.proxyView = self.tableView_2
        # self.proxyView.setAlternatingRowColors(True)
        # self.proxyView.setModel(self.proxyModel)
        self.tableView_2.setModel(self.proxyModel2)
        self.tableView_2.setAlternatingRowColors(True)
        self.tableView_2.setSortingEnabled(True)

        self.lineEdit_search.textChanged.connect(self.textFilterChanged)
        self.dateEdit.dateChanged.connect(self.dateFilterChanged)
        self.dateEdit_2.dateChanged.connect(self.dateFilterChanged)

    # def filter_date(self):
    #     combo_date = self.dateEdit.text()
    #     combo_date2 = self.dateEdit.text()
    #     filter = "cast(datetime1 as datetime)between cast('{}' as datetime) and cast('{}' as datetime)".format(
    #         combo_date, combo_date2)

    def dateFilterChanged(self):
        self.proxyModel2.setFilterMinimumDate(self.dateEdit.date())
        self.proxyModel2.setFilterMaximumDate(self.dateEdit_2.date())

    def textFilterChanged(self):
        # syntax = QRegExp.PatternSyntax(
        #     self.filterSyntaxComboBox.itemData(
        #         self.filterSyntaxComboBox.currentIndex()))
        caseSensitivity = Qt.CaseInsensitive
        regExp = QRegExp(self.lineEdit_search.text(), caseSensitivity)
        self.proxyModel2.setFilterRegExp(regExp)

    #########   FILTER ROW  ##########
    def get_filtered_rows(self):
        print("rows in fitered view is {} ".format(self.proxyModel2.rowCount()))
        print("rows in original model is {}".format(self.db_model2.rowCount()))

    def last_col_filtered(self):
        """Gets all the data from the filtered model and returns last column i.e total hours """
        data = []
        for row in range(self.proxyModel2.rowCount()):
            data.append([])
            for column in range(self.proxyModel2.columnCount()):
                index = self.proxyModel2.index(row, column)
                data[row].append(str(self.proxyModel2.data(index)))
            data2 = [col[5] for col in data]
        # print(data)
        print(data2)
        return data2

    def convert_last_col_filtered(self):
        date = [datetime.strptime(x, "%H:%M:%S") for x in self.last_col_filtered()]
        liste1 = []
        for i in date:
            dt = timedelta(hours=i.hour, minutes=i.minute, seconds=i.second)
            liste1.append(dt)
        return (sum(liste1, timedelta()))

    def proxy_hours_minutes(self):
        """conversion of time delta get_tot_hours to hours"""
        td = self.convert_last_col_filtered()
        resultat = td.days * 24 + td.seconds // 3600, (td.seconds // 60) % 60
        print('{} H {} M'.format(*resultat))
        return resultat

    def update_combobox_pilots(self):
        # Filling combox _avion
        query_aircraft = QSqlQuery("SELECT immatriculation FROM Aircraft")
        liste_ac = []
        while query_aircraft.next():
            aircraft = query_aircraft.value(0)
            liste_ac.append(aircraft)
        # self.comboBox_avion.addItems(liste_ac)
        # self.comboBox_sel_ac.addItems(liste_ac)
        return liste_ac

    def get_tot_hours(self):
        """select dates from database """
        query1 = QSqlQuery("SELECT date_time1,date_time2 FROM Pilots_hours")
        liste = []
        while query1.next():
            date1 = query1.value(0)
            date2 = query1.value(1)
            essai = datetime.strptime(date2, "%Y/%m/%d %H:%M") - datetime.strptime(date1, "%Y/%m/%d %H:%M")
            liste.append(essai)
        total = sum(liste, timedelta())
        return total

    def hours_minutes(self):
        """conversion of time delta get_tot_hours to hours"""
        td = self.get_tot_hours()
        # td = self.convert_last_col_filtered()
        resultat = td.days * 24 + td.seconds // 3600, (td.seconds // 60) % 60
        print('{} H {} M'.format(*resultat))
        return resultat

    def get_hours_diff(self):
        query1 = QSqlQuery("SELECT date_time1,date_time2 FROM Pilots_hours")
        result = []
        while query1.next():
            date1 = query1.value(0)
            date2 = query1.value(1)
            diff = datetime.strptime(date2, "%Y/%m/%d %H:%M") - datetime.strptime(date1, "%Y/%m/%d %H:%M")
            result.append(str(diff))
        return result

    @pyqtSlot()
    def on_pushButton_clicked(self):
        self.add_record()

    def add_record(self):
        row = self.db_model2.rowCount()
        print(row)
        self.db_model2.insertRow(row)

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

    @pyqtSlot()
    def on_pushButton_update_clicked(self):
        self.update_record()
        self.label.setText('{} H {} M'.format(*self.proxy_hours_minutes()))


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


class MySortFilterProxyModel2(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(MySortFilterProxyModel2, self).__init__(parent)

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
        # print(QDate().fromString(self.sourceModel().data(index2),"yyyy/MM/dd HH:mm"))
        # print(self.dateInRange(QDate().fromString((self.sourceModel().data(index2)))))
        # print( datetime.strptime(self.sourceModel().data(index2), "%Y/%m/%d %H:%M"))

        return ((self.filterRegExp().indexIn(self.sourceModel().data(index0)) >= 0
                 or self.filterRegExp().indexIn(self.sourceModel().data(index1)) >= 0)
                and self.dateInRange(self.sourceModel().data(index2)))
        # self.dateInRange(datetime.strptime(self.sourceModel().data(index2),"%Y/%m/%d %H:%M")))

        # self.dateInRange(self.sourceModel().data(QDate.fromString(str(index2)),"yyyy/MM/dd")))

    def dateInRange(self, date):
        # if isinstance(date,str):
        #
        #     date = datetime.strptime(date, "%Y/%m/%d %H:%M")
        #
        #
        # return ((not self.minDate.isValid() or date >= self.minDate)
        #         and (not self.maxDate.isValid() or date <= self.maxDate))

        try:
            date = datetime.strptime(date, "%Y/%m/%d %H:%M")
        except ValueError:
            pass

        return ((not self.minDate.isValid() or date >= self.minDate)
                and (not self.maxDate.isValid() or date <= self.maxDate))


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        form = MainWindow2()
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
