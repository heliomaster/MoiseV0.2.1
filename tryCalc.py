from datetime import datetime

from DB import *
import sqlite3
import pandas as pd

print('marche')


class CalculateFromSql:
    def __init__(self):

        self.con = sqlite3.connect("LmtPilots.db")
        self.query = "SELECT * FROM Pilots_hours;"
        self.df = pd .read_sql_query(self.query, self.con, parse_dates=['date_time1', 'date_time2'])
        print(f'this is it {self.df}')

    def essai(self):
        self.df2 =  pd.read_sql_query(self.query,self.con)



    # def essai(self):

        #
        # self.df = pd.read_sql_query(('select "Timestamp","Value" from "Pilots_hours" '
        #                      'where "Timestamp" BETWEEN %s AND %s'),query,
        #                    params=[datetime(2014,6,24,16,0),datetime(2014,6,24,17,0)],
        #                    index_col=['Timestamp'])
        # print (self.df)
        # return self.df






bibi = CalculateFromSql()
bibi
