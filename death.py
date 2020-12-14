import sqlite3
import json
import os
import requests

#Database setup
def setUpDatabase(db_name):
    ''' This function sets up a database. It will return a cursor and connector. '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ db_name)
    cur = conn.cursor()
    return cur, conn

def create_month_table(cur, conn):
    ''' This function takes in cursor and connector (cur and conn) and creates a table within the 
    database that has the name of the month. This function will be used to retrive the name of the month and 
    insert it into the death table to allow for easier calculations. '''
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
    ''' This function takes in cur and conn as parameters and creates the table for COVID 
    death data (total deaths and new deaths confirmed), located in the database. '''
    cur.execute('CREATE TABLE IF NOT EXISTS DEATH (key TEXT PRIMARY KEY, date TEXT UNIQUE, month TEXT, death INTEGER, deathConfirmed)')
    conn.commit()

def get_data():
    ''' This function creates the URL for the API request. It requires information on 
    the state- michigan (in the US) for which data will be gathered. It returns the data. ''' 
    base_url = "https://api.covidtracking.com/v1/states/mi/daily.json"
    r = requests.get(base_url)
    data = json.loads(r.text)
    return data

def add_to_death_table(cur,conn,lst):
    ''' This function creates a list of strings for months May - October. 
    This function loops adds the necessary data to the Death table. For each date in the time period,
    it adds a key, date (2020MONTHDAY), individual months (May- October), total deaths in michigan to date, and new confirmed deaths in michigan to date. 
    This function adds 25 unique pieces of data into the table at a time. '''
    stringLst = ["05", "06", "07","08","09","10"]
    cur.execute('SELECT COUNT(*) FROM DEATH')
    rows = cur.fetchone()[0]
    final = rows + 25
    for i in range(len(lst)):
        if rows < final and rows <= len(lst):
            if str(lst[i]["date"])[4:6] in stringLst:
                deathConfirmed = lst[i]["deathConfirmed"]- lst[i + 1]["deathConfirmed"]
                totalDeath = lst[i]["death"]
                date = lst[i]["date"]
                cur.execute('SELECT month_name FROM Months WHERE key = ?', (str(date)[4:6],))
                month = cur.fetchone()[0]
                cur.execute("INSERT OR IGNORE INTO DEATH (key, date, month, death, deathConfirmed) VALUES (?, ?, ?, ?, ?)", 
                (rows, date, month, totalDeath, deathConfirmed))
                cur.execute('SELECT COUNT(*) FROM DEATH')
                rows = cur.fetchone()[0]
                i = i + 1
        conn.commit()

def keep_running(cur, conn, lst):
    ''' This function asks the user if they would like to add the next 25 rows 
    to the table. If the user inputs no, it ends the program. If the user inputs
    yes, it adds the next 25 unique rows of data, and asks if it should input 25 more. When 
    there is no more data to input, the program prints "Data input complete" and exits the 
    program. '''
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
    ''' This function sets up the database and tables, stores information in dictionary,
    loops through dictionary and adds appropriate data to death table, 25 unique items at a time. '''
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('covid_tracking.db')
    #create_month_table(cur, conn)
    create_death_table(cur, conn)
    lst = get_data()
    #add_to_death_table(cur,conn,lst)
    keep_running(cur,conn,lst)

if __name__ == "__main__":
    main()

