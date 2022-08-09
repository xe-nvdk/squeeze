from fastapi import FastAPI
from typing import Any, Optional
from pydantic import BaseModel
import psycopg2 as psql
from config import config
import os
import datetime

# Defining the schema to save a new site in the database
class asset(BaseModel):
    name: str
    host: str
    port: int
    interval: int
    
class endpoint(BaseModel):
    name: str
    url: str
    token: str
    enable: bool
    
vibora = FastAPI()

# posting a new site to the database in a tablet called sites
@vibora.post("/api/v1/write")
async def write(asset: asset):
    try:      
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psql.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute("INSERT INTO sites (name, host, port, interval, date) VALUES (%s, %s, %s, %s, %s)", (asset.name, asset.host, asset.port, asset.interval, datetime.datetime.now()))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psql.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return {"message": "Site added to the database"}

# read all sites from the database in a tablet called sites and execute a ping command

@vibora.get("/api/v1/query/")
async def check_site(name: str):
    # read connection parameters
    params = config()
    # connect to the PostgreSQL server
    conn = psql.connect(**params)
    # create a cursor
    cur = conn.cursor()
    # query site from the database
    cur.execute("SELECT * FROM sites WHERE name = %s", (name,))
    row = cur.fetchone()
    return {"sites": row}
    # close communication with the database
    cur.close()
    
@vibora.get("/api/v1/ping")
async def ping(name: str):
    # read connection parameters
    params = config()
    # connect to the PostgreSQL server
    conn = psql.connect(**params)
    # create a cursor
    cur = conn.cursor()
    # query url from the database
    url = cur.execute("SELECT url FROM sites WHERE name = %s", (name,))
    url = cur.fetchone()
    port = cur.execute("SELECT port FROM sites WHERE name = %s", (name,))
    port = cur.fetchone()
    netcat = os.system("nc -z " + url[0] + " " + str(port[0]))
    cur.execute("CREATE TABLE IF NOT EXISTS checks (id BIGSERIAL, name TEXT, url TEXT, port INT, status INT, date TIMESTAMP)")
    cur.execute("INSERT INTO checks (name, url, port, status, date) VALUES (%s, %s, %s, %s, %s)", (name, url[0], port[0], netcat, datetime.datetime.now()))
    conn.commit()
    if netcat == 0:
        return {"message": "Site is up"}
    else: 
        return {"message": "Site is down"}
    
# Save notification endpoinbts to the database in a tablet called endpoints
@vibora.post("/api/v1/endpoints/create")
async def create_endpoint(endpoint: endpoint):
    conn = None
    try:      
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psql.connect(**params)
        # create a cursor
        cur = conn.cursor()
         # execute a statement
        cur.execute("INSERT INTO endpoints (name, url, token, enable) VALUES (%s, %s, %s, %s)", (endpoint.name, endpoint.url, endpoint.token, endpoint.enable))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psql.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return {"message": "Endpoint added to the database"}