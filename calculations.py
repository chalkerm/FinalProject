
import requests
import json
import os
import sqlite3
import matplotlib
import matplotlib.pyplot as plt 




def setUpDatabase(db_name):
    '''creates a new database with the passed in database name and returns cur,conn'''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def cases_calculations(cur,conn):
    '''takes in cur,conn as input. reates a list of the months from the month_num column in months2 table.
     returns a dictionary named newCases_dict where the key is the month_num from months2 table and the value is the total new cases from that month 
     the total new cases are calculated by adding up the new_cases column from that specific month by joining Cases and months2 tables '''
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



def recovered_dictionary(cur, conn):
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
    '''takes in a filename and 3 dictionaries where the key is the month and the value is the total. the function 
    writes to the filename the total cases,deaths, and recoveries for each month. the function doesn't return anything.'''

    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), filename), 'w') as f:
        i = 0
        months = d.keys()
        months_list = []
        for month in months:
            months_list.append(month)
        
        for month in data:
            f.write("Total COVID Cases for {} 2020: {} \n".format(months_list[i], data[month]))
            i+=1
        f.write("========================================\n")
        for item in dic:
            f.write("Total Deaths from COVID for {} 2020: {} \n".format(item, dic[item]))
        f.write("========================================\n")
        for x in d:
            f.write("Total Recoveries from COVID for {} 2020: {} \n".format(x, d[x]))
        


def graphs(cases_data,recov_d):
    '''takes 3 dictionaries as input, each have the month as they key, and the value as the total for that month'''
    '''the function creates 3 subplots displayed in 1 column, 3 rows'''
    '''the function doesn't return anything but it shows the graphs and saves them as a png to COVID_graphs.png'''

    fig = plt.figure(figsize=(5,10))
   


    # data and graph for Cases 
    names = []
    values = []
    for thing in cases_data:
        month = thing[5:]
        case_total = cases_data[thing]
        names.append(month)
        values.append(case_total)


    cases = fig.add_subplot(311)
    cases.grid()
    cases.plot(names,values, color = 'purple', marker = '*')
    cases.set_xlabel('Month', color = 'purple')
    cases.set_ylabel('Cases', color = 'purple')
    cases.set_title('Number of COVID-19 Cases by Month in 2020', color = 'purple')
    cases.set_ylim(0,60000)
   

    # recoveries graph 
    recov = fig.add_subplot(312)
    x = recov_d.keys()
    names2 = []
    values2 = []
    for thing in x:
        names2.append(thing)
    y = recov_d.values()
    for item in y:
        values2.append(item)
    recov.plot(names2, values2, color='blue', marker = 'D')
    recov.set_xlabel('Month Name', color='blue')
    recov.set_ylabel('Number of Recovered Cases', color='blue')
    recov.set_title('Number of COVID-19 Recoveries by Month in 2020', color='blue')
    recov.set_ylim(0,60000)
    for x,y in zip(names2,values2):
        anno = '{}'.format(y)
        plt.annotate(anno, (x,y), textcoords='offset points', xytext=(0, 10), ha='center')


  
    # deaths graph 
    deaths = fig.add_subplot(313)


    plt.tight_layout()
    # plt.show()
    # fig.savefig("COVID_graphs.png")

    # stacked bar graph of deaths vs recoveries
    figure, ax = plt.subplots()
    #ax = fig.add_subplot(314)
    width = 0.35
    labels = names2
    deaths = values # using cases until deaths ready
    recoveries = values2
    ax.bar(labels, deaths, width, label='Deaths', color='red')
    ax.bar(labels, recoveries, width, bottom=deaths, label='Recoveries', color='blue')
    ax.set_ylabel('Number of Deaths')
    ax.set_xlabel("Month Name")
    ax.legend()
    
    plt.show()
    



def main():
    cur,conn = setUpDatabase('covid_tracking.db')
    data = cases_calculations(cur,conn)
    d = recovered_dictionary(cur,conn)

    # deaths dict goes here
    dic = {}


    graphs(data,d)
    write_calculations("calculations_outfile", d,data,dic)
    

if __name__ == "__main__":
    main()
