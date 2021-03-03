from DB import *
import sqlite3
import pandas as pd

print('marche')

class calculateFromSql():
    def __init__(self):

        con = sqlite3.connect("LmtPilots.db")
        query = "SELECT * FROM Pilots_hours;"
        self.df = pd .read_sql_query(query,con, parse_dates=['date_time1', 'date_time2'])
        print(f'this is it {self.df}')

bibi = calculateFromSql()
bibi

