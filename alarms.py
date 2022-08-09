# Alarm setup and management for Vibora

import psycopg2 as psql
from config import config
import os
import datetime
import telepot

def alarm_trigger():
        params = config()
        # connect to the PostgreSQL server
        conn = psql.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # query status column from table checks and select last value
        cur.execute("SELECT status FROM checks ORDER BY id DESC LIMIT 1")
        status = cur.fetchone()
        print(status)
        # Select site
        name = "cduser.com"
        cur.execute("SELECT url from Sites WHERE url = %s", (name,))
        site = cur.fetchone()
        print(site)
        if status != (0,):
                bot.sendMessage(telegram_channel, "The host " + site[0] + " not responded in the last check")
                
alarm_trigger()

