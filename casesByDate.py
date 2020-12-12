import requests
import json
import unittest
import os
import sqlite3



    
def get_data():
    ''' this funciton tries to request the data from the API if there is an error it prints "error when requesting data from API" 
     and creates an empty dict. if the request is successful, the function loops through the data and adds only the data from 
    the months May through October to a list named MayThruOct and returns the list.'''
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
    '''this function calls get_data() and loops through the data and creates a list of tuples and returns it.
     Each tuple includes (date, total cases, new cases)
     the date should be a string in the form of 2020-MM-DD
    total cases should become an int and new cases should become a real'''
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
    '''creates a new database with the passed in database name and returns cur,conn'''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def month_table(cur,conn):
    '''this function takes in cur,conn and loops through data returned from clean_data() and creates a list called month_list of all the unique month numbers
     creates a new table named months with two columns:
    (1) month_id (integer primary key)
    (2) month_num (text)
    the function doesn't return anything. '''
    data = clean_data() 
    month_list= []
    for tple in data:
        month = tple[0][0:7]
        if month not in month_list:
            month_list.append(month)
    
    cur.execute("CREATE TABLE IF NOT EXISTS months2 (month_id INTEGER PRIMARY KEY,month_num TEXT)")
    for i in range(0,len(month_list)):
        cur.execute("INSERT INTO months2 (month_id,month_num) VALUES (?,?)", (i,month_list[i],))
    conn.commit()



def add_data_to_table(cur,conn):
    ''' the input is in cur,conn. the function adds data (25 items at a time) returned from the clean_data() function to a new table named Cases with five columns: 
    (1) id (integer primary key)
    (2) month_id (text) HINT: Found from the months2 table 
    (3) date (text in form of 2020-DD-MM)
    (4) new_cases (integer)
    (5) total_cases (integer)
    the function also calls month_table() only when Cases is empty.
    the function doesn't return anything'''
    data = clean_data()
    cur.execute('CREATE TABLE IF NOT EXISTS Cases (id INTEGER PRIMARY KEY, month_id INTEGER, date TEXT, new_cases INTEGER, total_cases INTEGER)')
    data2 = data[5:]
    cur.execute("SELECT id FROM Cases")
    lst = cur.fetchall()

    # only will happen the first time ran (when len(lst) == 0)
    start = 0 
    

    if len(lst) > 0:
        start = int(lst[-1][0]) + 1
    
    if start == 0:
        month_table(cur,conn)
    
   
    end = start + 25 

    i = 0
    for i in range(start,end):
         if i >= len(data2):
             i = i - 1
             break
         else:
            month_num = data2[i][0][0:7]
            cur.execute("SELECT month_id FROM months2 WHERE month_num = ?", (month_num,))
            month_id = cur.fetchone()[0]
            date = data2[i][0]
            total_cases = data2[i][1]
            new_cases = data2[i][2]
            cur.execute("INSERT INTO Cases (id, month_id,date,new_cases, total_cases) VALUES (?,?,?,?,?)",( i, month_id,date, new_cases,total_cases,))
    conn.commit()

    print("======================================")
    print("entered more items into database, you now have " + str(i + 1) + " items in the database\n")
    print("there is a total of " + str(len(data2)) + " items that you are able to put into the db\n")
    print("please run again to put more items in the db\n")
    print("======================================")





def main():
    cur,conn = setUpDatabase('covid_tracking.db')
    add_data_to_table(cur,conn)

    
if __name__ == "__main__":
    main()
    # unittest.main(verbosity=2)
