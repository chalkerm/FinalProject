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
    cur.execute('CREATE TABLE IF NOT EXISTS DEATH (key TEXT PRIMARY KEY, date TEXT UNIQUE, month TEXT, death INTEGER, deathProbable INTEGER, deathConfirmed)')
    conn.commit()

def get_data():
    ''' This function creates the URL for the API request. It requires information on 
    the state- Michigan (in the US) for which data will be gathered.'''
    base_url = "https://api.covidtracking.com/v1/states/mi/daily.json"
    r = requests.get(base_url)
    data = json.loads(r.text)
    return data

def add_to_death_table(cur,conn,lst):
    stringLst = ["05", "06", "07","08","09","10"]
    cur.execute('SELECT COUNT(*) FROM DEATH')
    rows = cur.fetchone()[0]
    final = rows + 25
    for i in range(len(lst)):
        if rows < final and rows <= len(lst):
            if str(lst[i]["date"])[4:6] in stringLst:
                deathConfirmed = lst[i]["deathConfirmed"]
                deathProbable = lst[i]["deathProbable"]
                death = lst[i]["death"]
                date = lst[i]["date"]
                cur.execute('SELECT month_name FROM Months WHERE key = ?', (str(date)[4:6],))
                month = cur.fetchone()[0]
                cur.execute("INSERT OR IGNORE INTO DEATH (key, date, month, death, deathProbable, deathConfirmed) VALUES (?, ?, ?, ?, ?, ?)", 
                (rows, date, month, death, deathProbable, deathConfirmed))
                cur.execute('SELECT COUNT(*) FROM DEATH')
                rows = cur.fetchone()[0]
                i = i + 1
        conn.commit()

def keep_running(cur, conn, lst):
    x = input("Would you like to add 25 rows? Please enter 'yes' or 'no'.")
    while x != 'no':
        cur.execute('SELECT COUNT(*) FROM DEATH')
        row = cur.fetchone()[0]
        if row + 25 > 185:
            add_to_death_table(cur, conn, lst)
            print("Data input complete")
            break
        else:
            add_to_death_table(cur, conn, lst)
            x = input("Would you like to add 25 rows? Please enter 'yes' or 'no'.")


def main():
    # SETUP DATABASE AND TABLE
        cur, conn = setUpDatabase('covid_tracking.db')
        #create_month_table(cur, conn)
        create_death_table(cur, conn)
        lst = get_data()
        #add_to_death_table(cur,conn,lst)
        keep_running(cur,conn,lst)

if __name__ == "__main__":
    main()

