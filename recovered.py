import sqlite3
import json
import os
import requests

# Create Database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ db_name)
    cur = conn.cursor()
    return cur, conn

def create_month_table(cur, conn):
    cur.execute('CREATE TABLE Months (key TEXT PRIMARY KEY, month_name TEXT)')
    i = 1
    month_lst = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    while i <= 12:
        for month in month_lst:
            if len(str(i)) == 1:
                new = '0' + str(i)
            else:
                new = str(i)
            cur.execute("INSERT INTO Months (key, month_name) VALUES (?, ?)", (new, month))
            i += 1
    conn.commit()

def create_recovered_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Recovered (key TEXT PRIMARY KEY, date TEXT UNIQUE, month TEXT, new_recovered INTEGER, total_recovered INTEGER)')
    conn.commit()

def create_request_url(state, start_date, end_date):
    ''' Date should be in the format YYYY-MM-DD '''
    base_url = "https://api.covid19tracking.narrativa.com/api/country/us"
    url = base_url + '/region/{}?date_from={}&date_to={}'.format(state, start_date, end_date)
    return url

def get_data():
    current_month = 5
    end_month = current_month + 1
    d = {}
    d['dates'] = {}
    while end_month <= 11:
        new_month = str(current_month)
        if len(new_month) == 1:
            new_month = '0' + new_month
        new_end_month = str(end_month)
        if len(new_end_month) == 1:
            new_end_month = '0' + new_end_month
        request_url = create_request_url('michigan', '2020-{}-01'.format(new_month), '2020-{}-01'.format(new_end_month))
        r = requests.get(request_url)
        data = json.loads(r.text)
        for day in data['dates']:
            if day not in d['dates']:
                d['dates'][day] = data['dates'][day]
        current_month += 1
        end_month += 1
    return d

    
def add_recovered_data(cur, conn, d):
    counter = 0
    while counter < len(d['dates']):
        i = 0
        while i < 25:
            for date in d['dates']:
                day = date
                new_recovered = d['dates'][date]['countries']['US']['today_new_recovered']
                total_recovered = d['dates'][date]['countries']['US']['today_recovered']
                cur.execute('SELECT month_name FROM Months WHERE key = ?', (day[5:7],))
                month = cur.fetchone()[0]
                cur.execute("INSERT INTO Recovered (key, date, month, new_recovered, total_recovered) VALUES (?, ?, ?, ?, ?)", 
                (counter, day, month, new_recovered, total_recovered))
                counter += 1
                i += 1
        conn.commit()

def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('covid_tracking.db')
    create_month_table(cur, conn)
    create_recovered_table(cur, conn)
    dic = get_data()
    add_recovered_data(cur, conn, dic)

if __name__ == "__main__":
    main()
    
