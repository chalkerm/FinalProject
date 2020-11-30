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
    base_url = "https://api.covid19tracking.narrativa.com/api/country/us/"
    url = base_url + '/region/{}?date_from={}&date_to={}'.format(state, start_date, end_date)
    return url

def add_data(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Recovered (key TEXT PRIMARY KEY, date TEXT, new_recovered INTEGER, total_recovered INTEGER)')
    request_url = create_request_url('michigan', '2020-04-12', '2020-11-12')
    r = requests.get(request_url)
    d = json.loads(r.text)
    counter = 0
    while counter < len(d['dates']):
        for date in d['dates'][counter:counter + 25]:
            day = date
            new_recovered = d['dates'][date]['countries']['US']['today_new_recovered']
            total_recovered = ['dates'][date]['countries']['US']['today_recovered']
            cur.execute("INSERT INTO Recovered (key, date, new_recovered, total_recovered) VALUES (?, ?, ?, ?)", 
            (counter, day, new_recovered, total_recovered))
            counter += 1
        conn.commit()

def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('covid_tracking.db')
    add_data(cur, conn)

if __name__ == "__main__":
    main()
    