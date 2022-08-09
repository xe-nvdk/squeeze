import psycopg2 as psql
from config import config
import logging
import secrets
import datetime

logging.basicConfig(filename='auth.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
params = config()
conn = psql.connect(**params)
cur = conn.cursor()

def first_token():
    try:
        token_generator = secrets.token_urlsafe(64)
        permissions = 'RW'
        cur.execute("SELECT token FROM auth_token")
        check = cur.fetchall()
        if check == []:
            cur.execute("INSERT INTO auth_token (token, permissions, date) VALUES (%s, %s, %s)", (token_generator, permissions, datetime.datetime.now()))
            conn.commit()
            logging.info('The first token was created')
        else:
            logging.warn('The first token already exists')
    except:
        logging.error('Could not save the first token please, check the database connection in the file config.ini')
        