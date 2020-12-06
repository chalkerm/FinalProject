import requests
import json
import unittest
import os
import sqlite3

def month_table(cur,conn):
    #creates a new table named months with three columns:
    # (1) month_id (integer primary key)
    # (2) month_num (text) 
    # (2) month (text) 
    months = ["May", "June", "July", "August", "September", "October"]
    num_months = ["05","06","07", "08","09","10"]
    cur.execute("CREATE TABLE IF NOT EXISTS months (month_id INTEGER PRIMARY KEY,month_num TEXT, month TEXT)")
    for i in range(0,len(months)):
        cur.execute("INSERT INTO months (month_id,month_num,month) VALUES (?,?,?)", (i,num_months[i], months[i],))
    conn.commit()

    
def get_data():
    # tries to request the data from the API if there is an error it prints "error when requesting data from API" 
    # and creates an empty dict. if the request is successful, the function loops through the data and adds only the data from 
    # the months May through October to a list named MayThruOct and returns the list.
    try:
        # get the data from the url only from MI 
        url = "https://data.cdc.gov/resource/9mfq-cb36.json?state=MI"
        data1 = requests.get(url)
        data2 = data1.text
        data = json.loads(data2)
    except:
        print("error when requesting data from API")
        data = {}
    if len(data) > 0:
        mayThruOct = []
        # make new list of only data that was during may-oct
        for thing in data:
            if thing["created_at"][5:7] != '03' and thing["created_at"][5:7] != '04' and thing["created_at"][5:7] != '11' and thing["created_at"][5:7] != '12' :
                mayThruOct.append(thing)
    # return list of data from may-oct
    if len(data) == 0:
        print("error")
    
    return mayThruOct

def clean_data():
    # takes returned data from get_data() and creates a list of tuples and returns it.
    # Each tuple includes (date, total cases, new cases)
    # the date should be a string in the form of 2020-DD-MM
    # total cases should become an int and new cases should become a real
    tuples = []
    data = get_data()
    for thing in data:
        x = thing["created_at"][0:10]
        y = int(thing["tot_cases"])
        z = float(thing["new_case"])
        tple = (x,y,z)
        tuples.append(tple)
    return tuples


def setUpDatabase(db_name):
    # creates a new database with the passed in database name
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def add_data_to_table(cur,conn):
    # adds data returned from the clean_data() function to a new table named Cases with four columns: 
    # (1) month_id (text) HINT: Found from the months table 
    # (2) date (text in form of 2020-DD-MM)
    # (3) new_cases (integer)
    # (4) total_cases (integer)
    # NOTE: Adds 25 items to the table at a time 
    data = clean_data()
    cur.execute('CREATE TABLE IF NOT EXISTS Cases (month_id INTEGER, date TEXT, new_cases INTEGER, total_cases INTEGER)')
    
    count = 5  
    # needed to start count at 5 because I didn't want the first 5 items in the data set
    while count < len(data):
        i = 0 
        while i < 25:
            if count >= len(data):
                break
            else:
                month_num = data[count][0][5:7]
                cur.execute("SELECT month_id FROM months WHERE month_num = ?", (month_num,))
                month_id = cur.fetchone()[0]
                date = data[count][0]
                total_cases = data[count][1]
                new_cases = data[count][2]
                cur.execute("INSERT INTO Cases (month_id,date,new_cases, total_cases) VALUES (?,?,?,?)",(month_id,date, new_cases,total_cases,))
                count += 1
                i += 1
    conn.commit()



def main():
    cur,conn = setUpDatabase('casesByDate.db')
    month_table(cur,conn)
    add_data_to_table(cur,conn)

    
if __name__ == "__main__":
    main()
    # unittest.main(verbosity=2)
