#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5.QtSql import *


class LmtDataBase():

    def __init__(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("LmtPilots.db")

        self.db.open()

        query = QSqlQuery()
        # query.exec_('''CREATE TABLE Pilots(id INTEGER PRIMARY KEY,pilot_1 TEXT, datetime1 TEXT, datetime2 TEXT,pilot_mail TEXT)''')
        query.exec_('''CREATE TABLE Pilots_exp(id INTEGER PRIMARY KEY UNIQUE , pilot_1 TEXT, nia_pilot TEXT, contrat_reserve TEXT, vsa TEXT,
                      cempn TEXT, ctl_tactique TEXT,ctl_aeroclub TEXT,sep TEXT, habilitation_cd TEXT, licence TEXT, pilot_mail TEXT, jours_restants INTEGER)''')

        query.exec_('''CREATE TABLE Pilots_hours(id INTEGER PRIMARY KEY UNIQUE , pilot_1 TEXT,pilot_2 TEXT,aircraft INTEGER,
             date_time1 TEXT DEFAULT '1973/01/06 10:30', date_time2 TEXT DEFAULT '1973/01/06 10:30', total TEXT,mission TEXT DEFAULT 'sans objet',commentaires TEXT)''')

        query.exec(
            '''CREATE TABLE Pilots_id(id INTEGER PRIMARY KEY UNIQUE, rank TEXT, first_name TEXT, last_name TEXT,nia TEXT)''')

        query.exec_(
            '''CREATE TABLE Aircraft(id INTEGER PRIMARY KEY, immatriculation TEXT,type_ac TEXT,puissance TEXT,prix TEXT)''')



        query.exec_("""INSERT INTO Pilots_exp (id ,pilot_1 , nia_pilot , contrat_reserve , vsa ,cempn , ctl_tactique ,ctl_aeroclub ,sep ,
 habilitation_cd , licence , pilot_mail , jours_restants)  VALUES ( 1,'NOM','AA12345','2030/01/01',
  '2030/01/01','2030/01/01','2030/01/01', '2030/01/01','2030/01/01','2030/01/01','2030/01/01','email@email.com', 20)""""")

        query.exec_('''INSERT INTO Pilots_hours (id ,pilot_1,pilot_2, aircraft, date_time1 , date_time2, total mission, mission, commentaires )  VALUES 
            ( 1,'NOM','NOM ',1','2030/01/01 15:00','2030/01/01 15:00', '0','une mission super importante qui va sauver le monde','sans commentaire')''')

        query.exec_('''INSERT INTO Aircraft(id, immatriculation,type_ac,puissance,prix) VALUES (1, 'F-GTPH','DR400','180','180')''')

        query.exec_(
            '''INSERT INTO Pilots_id(id,rank,first_name,last_name,nia) VALUES (1,'CAPITAINE','MARC','MORGAND','AK10000')''')

        query.exec_()

        self.db.commit()
        self.db.close()


if __name__ == '__main__':
    LmtDataBase()
