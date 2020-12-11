import sqlite3
import json
import os
import requests

# Create Database
def setUpDatabase(db_name):
    ''' This function sets up a database in the current location. '''

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ db_name)
    cur = conn.cursor()
    return cur, conn

def create_month_table(cur, conn):
    ''' This function creates a table within the database that has the number of the 
    month (i.e. January is the first month, '01') and the name of the month. This function
    will be used to grab the name of the month and insert it into the recovered table 
    to allow for easier calculations late. '''

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
    ''' This function creates the table for COVID recovery data, located in the 
    database. '''

    cur.execute('CREATE TABLE IF NOT EXISTS Recovered (key TEXT PRIMARY KEY, date TEXT UNIQUE, month TEXT, new_recovered INTEGER, total_recovered INTEGER)')
    conn.commit()

# def create_data_by_month(cur, conn):
#     cur.execute('CREATE TABLE IF NOT EXISTS Monthly_Data (month TEXT, monthly_recovered INTEGER)')
#     conn.commit()

def create_request_url(state, start_date, end_date):
    ''' This function creates the URL for the API request. It requires information on 
    the state (in the US) for which data will be gathered, as well as a start date 
    and end date for the time period it will be getting data for. All required parameters
    should be strings.
    Date should be in the format YYYY-MM-DD '''

    base_url = "https://api.covid19tracking.narrativa.com/api/country/us"
    url = base_url + '/region/{}?date_from={}&date_to={}'.format(state, start_date, end_date)
    return url

def get_data():
    ''' This function executes the API request for each month in our designated time 
    period. The month must be in the form of a string for the API request url.
    After each execution, it adds the requested data to a dictionary. '''

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

# def get_monthly_data():
#     current_month = 5
#     end_month = current_month + 1
#     d = {}
#     while end_month <= 11:
#         new_month = str(current_month)
#         if len(new_month) == 1:
#             new_month = '0' + new_month
#         new_end_month = str(end_month)
#         if len(new_end_month) == 1:
#             new_end_month = '0' + new_end_month
#         request_url = create_request_url('michigan', '2020-{}-01'.format(new_month), '2020-{}-01'.format(new_end_month))
#         r = requests.get(request_url)
#         data = json.loads(r.text)
#         month = new_month
#         d[month] = data['total']['today_recovered']
#         current_month += 1
#         end_month += 1
#     return d

    
def add_recovered_data(cur, conn, d):
    ''' This function loops through the data from the dictionary returned in get_data
    and adds the necessary data to the Recovered table. For each date in the time period,
    it adds:
    1. a primary key (integer)
    2. date (string)
    3. month name (string selected from Month table)
    4. number of new people who recovered from COVID on that date
    5. total number of people recovered from COVID in Michigan to date
    This function adds 25 unique pieces of data into the table at a time. '''
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
    ''' This function asks the user if they would like to add the next 25 rows 
    to the table. If the user inputs no, it ends the program. If the user inputs
    yes, it adds the next 25 rows of data, and asks if it should input 25 more. If 
    there is no more data to input, it prints "Data input complete" and exits the 
    program. '''
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

# def add_month_totals(cur, conn, d):
#     for key in d:
#         month = key
#         total = d[key]
#         cur.execute("INSERT INTO Monthly_Data (month, monthly_recovered) VALUES (?, ?)", 
#             (month, total))
#     conn.commit()



def calculate_recovered_totals(cur, conn, month, filename):
    ''' This function calculates the total number of recovered cases for each month. '''
    total = 0
    cur.execute('SELECT new_recovered FROM Recovered WHERE month = ?', (month, ) )
    values = cur.fetchall()
    for tup in values:
        num = tup[0]
        total += num
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), filename), 'w') as f:
        f.write("Total Recoveries from COVID for {}: {}".format(month, total))


def main():
    # SETUP DATABASE AND TABLES
    cur, conn = setUpDatabase('covid_tracking.db')
    create_month_table(cur, conn)
    create_recovered_table(cur, conn)
    #create_data_by_month(cur, conn)
    # dic = get_data()
    #d = get_monthly_data()
    # keep_running(cur, conn, dic)
    #add_month_totals(cur, conn, d)
    calculate_recovered_totals(cur, conn, 'May', 'calculations_file')
    calculate_recovered_totals(cur, conn, 'June', 'calculations_file')
    calculate_recovered_totals(cur, conn, 'July', 'calculations_file')
    calculate_recovered_totals(cur, conn, 'August', 'calculations_file')
    calculate_recovered_totals(cur, conn, 'September', 'calculations_file')
    calculate_recovered_totals(cur, conn, 'October', 'calculations_file')

if __name__ == "__main__":
    main()
    
    
