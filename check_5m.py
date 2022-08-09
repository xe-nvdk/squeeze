import psycopg2 as psql
from config import config
import os
import datetime
import time
import logging

def check_300():
    params = config()
    interval = 300
    try:
        conn = psql.connect(**params)
    except (Exception, psql.DatabaseError) as error:
        exit()
# create a cursor
    cur = conn.cursor()
# define the number of checks based on ids in the table sites
    while True:
        try:
            cur.execute("SELECT name, host, port FROM sites WHERE interval = 300")
            host_port = cur.fetchall()
        except:
            exit()

        for i in range(len(host_port)):
            try:
                netcat = os.system('nc -z ' + host_port[i][1] + ' ' + str(host_port[i][2]))
            except:
                exit()
            try:
                curl = os.popen('curl -s -o /dev/null -w "%{time_total}" ' + host_port[i][1] + ':' + str(host_port[i][2])).read()
                response_time = format(float(curl)*1000, '.2f')
            except:
                exit()                    

            try:
                cur.execute("INSERT INTO checks (name, host, port, status, response_time, date) VALUES (%s, %s, %s, %s, %s, %s)", (host_port[i][0], host_port[i][1], host_port[i][2], netcat, response_time, datetime.datetime.now()))
                conn.commit()
            except:
                exit()
            
        time.sleep(interval)
