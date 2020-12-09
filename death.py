import sqlite3
import json
import os
import requests

#Database setup
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ db_name)
    cur = conn.cursor()
    return cur, conn

def create_month_table(cur, conn):
    cur.execute('CREATE TABLE Months (key TEXT PRIMARY KEY, month_name TEXT)')
    i = 1
    monthLst = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    while i <= 12:
        for month in monthLst:
            if len(str(i)) == 1:
                new = '0' + str(i)
            else:
                new = str(i)
            cur.execute("INSERT INTO Months (key, month_name) VALUES (?, ?)", (new, month))
            i += 1
    conn.commit()

def create_death_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS DEATH (key TEXT PRIMARY KEY, date TEXT UNIQUE, death INTEGER, deathProbable INTEGER, deathConfirmed)')
    conn.commit()

def get_data():
    ''' Date should be in the format YYYY-MM-DD '''
    base_url = "https://api.covidtracking.com/v1/states/mi/daily.json"
    r = requests.get(base_url)
    data = json.loads(r.text)
    return data

def add_to_death_table(cur,conn,lst):
    dic = {}
    stringLst = ["05", "06", "07","08","09","10"]
    cur.execute('SELECT COUNT(*) FROM DEATH')
    rows = cur.fetchone()[0]
    final = rows + 25
    for dic in lst:
        if rows < final and rows <= len(lst):
            if lst[dic]["date"][4:6] in stringLst:
                deathConfirmed = lst[dic]["deathConfirmed"]
                deathProbable = lst[dic]["deathProbable"]
                death = lst[dic]["death"]
                cur.execute("INSERT OR IGNORE INTO DEATH (key,date, death, deathProbable, deathConfirmed) VALUES (?, ?, ?, ?, ?)", 
                (rows, date, death, deathProbable, deathConfirmed))
                cur.execute('SELECT COUNT(*) FROM DEATH')
                rows = cur.fetchone()[0]
        conn.commit()


    def main():
    # SETUP DATABASE AND TABLE
        cur, conn = setUpDatabase('covid_tracking.db')
        #create_month_table(cur, conn)
        create_death_table(cur, conn)
        lst = get_data()
        add_to_death_table(cur,conn,lst)

if __name__ == "__main__":
    main()