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
    cur.execute('DROP TABLE IF EXISTS Months')
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

def create_data_by_month(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Monthly_Data (month TEXT, monthly_recovered INTEGER)')
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

def get_monthly_data():
    current_month = 5
    end_month = current_month + 1
    d = {}
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
        month = data['total']['date'][5:7]
        d[month] = data['total']['today_recovered']
        current_month += 1
        end_month += 1
    return d

    
def add_recovered_data(cur, conn, d):
    cur.execute('SELECT COUNT(*) FROM Recovered')
    row = cur.fetchone()[0]
    final = row + 25
    for date in d['dates']:
        if row < final and row <= len(d['dates']):
            day = date
            new_recovered = d['dates'][date]['countries']['US']['today_new_recovered']
            total_recovered = d['dates'][date]['countries']['US']['today_recovered']
            cur.execute('SELECT month_name FROM Months WHERE key = ?', (day[5:7],))
            month = cur.fetchone()[0]
            cur.execute("INSERT OR IGNORE INTO Recovered (key, date, month, new_recovered, total_recovered) VALUES (?, ?, ?, ?, ?)", 
            (row, day, month, new_recovered, total_recovered))
            cur.execute('SELECT COUNT(*) FROM Recovered')
            row = cur.fetchone()[0]
    conn.commit()


def keep_running(cur, conn, d):
    x = input("Would you like to add 25 rows? Please enter 'yes' or 'no'.")
    while x != 'no':
        cur.execute('SELECT COUNT(*) FROM Recovered')
        row = cur.fetchone()[0]
        if row + 25 > len(d['dates']):
            add_recovered_data(cur, conn, d)
            print("Data input complete")
            break
        else:
            add_recovered_data(cur, conn, d)
            x = input("Would you like to add 25 rows? Please enter 'yes' or 'no'.")

def add_month_totals(cur, conn, d):
    for key in d:
        month = key
        total = d[key]
        cur.execute("INSERT INTO Monthly_Data (month, monthly_recovered) VALUES (?, ?)", 
            (month, total))
    conn.commit()



def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('covid_tracking.db')
    create_month_table(cur, conn)
    create_recovered_table(cur, conn)
    create_data_by_month(cur, conn)
    dic = get_data()
    d = get_monthly_data()
    keep_running(cur, conn, dic)
    add_month_totals(cur, conn, d)

if __name__ == "__main__":
    main()
