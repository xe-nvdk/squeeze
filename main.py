import psycopg2 as psql
from config import config
import time
import logging
from multiprocessing import Process
from check_1m import check_60
from check_5m import check_300
from auth import first_token
import uvicorn


logging.basicConfig(filename='main.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
params = config()
conn = psql.connect(**params)
cur = conn.cursor()

# Start the API server
def start_api():
    uvicorn.run("api:vibora", host="0.0.0.0", port=8000, log_level="info", reload=False)

# Setup the tables
try:
    cur.execute("CREATE TABLE IF NOT EXISTS auth_token (id SERIAL, token TEXT PRIMARY KEY, permissions TEXT, date TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS checks (id BIGSERIAL, name TEXT, host TEXT, port INT, status INT, response_time FLOAT, date TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS sites (id BIGSERIAL, name TEXT, host TEXT, port INT, interval INT, date TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS endpoints (id SERIAL, name TEXT, url TEXT, token TEXT, enable BOOLEAN, date TIMESTAMP)")
    conn.commit()
    logging.info('The tables were created or already exists')
except:
    logging.error('Could not create the tables, please, check the database connection in the file database.ini')

# define the hosts to check based on the interval time
try:
    cur.execute("SELECT name FROM sites WHERE interval = 60")
    sites_60 = cur.fetchall()
    cur.execute("SELECT name FROM sites WHERE interval = 300")
    sites_300 = cur.fetchall()
    logging.info('60 seconds interval sites: ' + str(sites_60))
    logging.info('300 seconds (5 minutes) interval sites: ' + str(sites_300))
except:
    logging.info('No sites with 60 seconds interval')
    logging.info('No sites with 300 seconds interval')

try:
    first_token = Process(target=first_token)
    first_token.start()
    start_api = Process(target=start_api)
    start_api.start()
    check_60 = Process(target=check_60)
    check_60.start()
    check_300 = Process(target=check_300)
    check_300.start()
    logging.info('The processes were started and the API server is running')
except:
    logging.error('Could not start the processes, make sure that you have the right permissions to run the processes')
    

# fix 5m file.
# next thing play with api definitions in the api.py file.