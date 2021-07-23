import time
import psycopg2
from psycopg2 import Error
from datetime import datetime
import os

# the iss_module defines functions used below such as for opening url, 
# parsing station info, creating turtle object and defining users position
import iss_module

# APIs and DB connections in use

db_user = os.environ.get('SPACE_STATIONS_USER')
db_pwd = os.environ.get('SPACE_STATIONS_PWD')
db_host = os.environ.get('SPACE_STATIONS_HOST')
db_port = os.environ.get('SPACE_STATIONS_PORT')
db_db = os.environ.get('SPACE_STATIONS_DB')
private_key = os.environ.get('SPACE_STATIONS_APIKEY')

iss_api = "https://api.n2yo.com/rest/v1/satellite/positions/25544/51.48/-3.18/0/1/&apiKey="+str(private_key)
css_api = "https://api.n2yo.com/rest/v1/satellite/positions/48274/51.48/-3.18/0/1/&apiKey="+str(private_key)

# Retreiving current locations of ISS and Chinese Space Station
try:
    # Connect to an existing database
    connection = psycopg2.connect(user=db_user,
                                  password=db_pwd,
                                  host=db_host,
                                  port=db_port,
                                  database=db_db)

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    starting_time = current_time = datetime.now()
    time_since_start_seconds = 0

#data collection starts here and runs for 2 hours at a time

    while time_since_start_seconds<7200:
        iss_data = iss_module.opening_url(iss_api)
        css_data = iss_module.opening_url(css_api)

        postgres_insert_query = """ INSERT INTO public.space_stations (date_time,id,station,lat,lon) VALUES (%s,%s,%s,%s,%s)"""

        iss_to_insert = (iss_module.station_info(iss_data))
        css_to_insert = (iss_module.station_info(css_data))

        cursor.execute(postgres_insert_query, iss_to_insert)
        connection.commit() 
        cursor.execute(postgres_insert_query, css_to_insert)
        connection.commit()

        time.sleep(30)

        current_time = datetime.now()
        time_since_start = current_time-starting_time
        time_since_start_seconds = time_since_start.total_seconds()
        
except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")