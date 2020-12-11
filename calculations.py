
import requests
import json
import os
import sqlite3
import matplotlib
import matplotlib.pyplot as plt 




def setUpDatabase(db_name):
    # creates or finds a database with the passed in database name
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def cases_calculations(cur,conn):
    # creates a list of the months from the month_num column in months2 table called
    # returns a dictionary named newCases_dict where the key is the month_num from months2 table and the value is the total new cases from that month 
    # the total new cases are calculated by adding up the new_cases column from that specific month by joining Cases and months2 tables
    newCases_dict = {}
    cur.execute("SELECT month_num FROM months2")
    months = cur.fetchall()
    for i in range(len(months)):
        total = 0
        month = months[i][0]
        cur.execute("SELECT Cases.new_cases FROM Cases JOIN months2 ON Cases.month_id = months2.month_id WHERE months2.month_num = ?", (month,))
        month_nums = cur.fetchall()
        for i in range(len(month_nums)):
            total += month_nums[i][0]
        newCases_dict[month] = total   
    return newCases_dict

def graph_cases(data):
    names = []
    values = []
    for thing in data:
        month = thing[5:]
        case_total = data[thing]
        names.append(month)
        values.append(case_total)

    # fig,ax = plt.subplots()
    plt.grid()
    plt.plot(names,values, color = 'purple', marker = '*')
    plt.xlabel('Month', color = 'purple')
    plt.ylabel('Cases', color = 'purple')
    plt.title('Number of COVID-19 Cases by Month in 2020', color = 'purple')
    plt.show()

def calculate_recovered_totals(cur, conn, month, filename):
    ''' This function calculates the total number of recovered cases for each month. '''
    total = 0
    cur.execute('SELECT new_recovered FROM Recovered WHERE month = ?', (month, ) )
    values = cur.fetchall()
    for tup in values:
        num = tup[0]
        total += num
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), filename), 'w') as f:
        f.write("Total Recoveries from COVID for {}: {} \n".format(month, total))


def recovered_for_graphing(cur, conn):
    cur.execute('SELECT DISTINCT month FROM Recovered')
    data = cur.fetchall()
    months = []
    for info in data:
        months.append(info[0])
    d = {}
    for month in months[:-1]:
        cur.execute('SELECT new_recovered FROM Recovered WHERE month = ?', (month, ) )
        values = cur.fetchall()
        total = 0
        for tup in values:
            num = tup[0]
            total += num
        if month not in d:
            d[month] = total
    return d

def write_calculations(filename, d, data, dic):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), filename), 'w') as f:
        for month in data:
            f.write("Total COVID Cases for {} 2020: {} \n".format(month, data[month]))
        for item in dic:
            f.write("Total Deaths from COVID for {} 2020: {} \n".format(item, dic[item]))
        for x in d:
            f.write("Total Recoveries from COVID for {} 2020: {} \n".format(item, d[item]))
        

def graph_recovered(d):
    x = d.keys()
    y = d.values()
    plt.bar(x, y, color='blue')
    plt.xlabel('Month Name')
    plt.ylabel('Number of Recovered Cases')
    plt.show()




def main():
    cur,conn = setUpDatabase('covid_tracking.db')
    data = cases_calculations(cur,conn)
    graph_cases(data)
    d = recovered_for_graphing(cur,conn)
    write_calculations("calculations_outfile", d)
    graph_recovered(d)

if __name__ == "__main__":
    main()