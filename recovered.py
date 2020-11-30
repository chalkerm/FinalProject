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

def create_request_url(state, start_date, end_date):
    ''' Date should be in the format YYYY-MM-DD '''
    base_url = "https://api.covid19tracking.narrativa.com/api/country/us"
    url = base_url + '/region/{}?date_from={}&date_to={}'.format(state, start_date, end_date)
    return url

def add_data(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Recovered (key TEXT PRIMARY KEY, date TEXT UNIQUE, new_recovered INTEGER, total_recovered INTEGER)')
    current_month = 4
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
        request_url = create_request_url('michigan', '2020-{}-12'.format(new_month), '2020-{}-12'.format(new_end_month))
        r = requests.get(request_url)
        data = json.loads(r.text)
        for day in data['dates']:
            if day not in d['dates']:
                d['dates'][day] = data['dates'][day]
        current_month += 1
        end_month += 1
    counter = 0
    while counter < len(d['dates']):
        i = 0
        while i < 25:
            for date in d['dates']:
                day = date
                new_recovered = d['dates'][date]['countries']['US']['today_new_recovered']
                total_recovered = d['dates'][date]['countries']['US']['today_recovered']
                cur.execute("INSERT INTO Recovered (key, date, new_recovered, total_recovered) VALUES (?, ?, ?, ?)", 
                (counter, day, new_recovered, total_recovered))
                counter += 1
                i += 1
        conn.commit()

def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('covid_tracking.db')
    add_data(cur, conn)

if __name__ == "__main__":
    main()
    