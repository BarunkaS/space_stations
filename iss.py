import psycopg2
from psycopg2 import Error
from datetime import datetime
import os
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
import streamlit as st
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
people_api = "http://api.open-notify.org/astros.json"

# Connect to PostgreSQL that has historical space stations data
connection = psycopg2.connect(user=db_user,
                                password=db_pwd,
                                host=db_host,
                                port=db_port,
                                database=db_db)
cursor = connection.cursor()
cursor2 = connection.cursor()

# setting up layout
st.set_page_config(layout="wide")

row1_1, row1_2 = st.beta_columns((2,3))

with row1_1:
    st.title("Manned Space Stations Around Us")

with row1_2:
    st.markdown('**PLEASE NOTE:** This is an experimental app and work in progress. Visit the bottom page on what next steps are planned. Cheers, Barbora')

row2_1, row2_2 = st.beta_columns((4,2))

with row2_1:

    iss_data = iss_module.opening_url(iss_api)
    iss_list = {'lat': iss_module.station_info(iss_data)[3], 'lon': iss_module.station_info(iss_data)[4]}
    iss_current_position = pd.DataFrame(iss_list,index=[0])
 #   time_now = iss_data["timestamp"]

    css_data = iss_module.opening_url(css_api)
    css_list = {'lat': iss_module.station_info(css_data)[3], 'lon': iss_module.station_info(css_data)[4]}
    css_current_position = pd.DataFrame(css_list,index=[0])

    current_positions = pd.concat([iss_current_position,css_current_position])

    st.write("**Currently, two manned space stations orbit the Earth. The ISS and the Chinese space station. Their current position is below.**")
    st.write("NOTE: This map updates with fresh position every time the page is loaded.")
    st.map(current_positions)

with row2_2:
    # Information about people in space + user location
    people_data = iss_module.opening_url(people_api)

    people = people_data["people"]
    people_crafts = []

    for item in people:
        people_crafts.append(item["name"]+' on '+item["craft"])

    a = "**There are currently "+str(people_data["number"])+" astronauts in the space in total. They are: **"
    b = people_crafts
    c = "In case you were curious"
    d = "Your current location is: " + iss_module.my_position()

    st.write(a,b,c)
    st.write(d)

# second half shows former movements of the space stations


st.write("")
st.title("Where were the stations on a given date?")

cursor2.execute(""" SELECT MIN(date_time) FROM public.space_stations""")
dates_min_max = sqlio.read_sql_query(""" SELECT date(MIN(date_time)) as min, date(MAX(date_time)) as max FROM public.space_stations""", connection)

day_selection = str(st.date_input("Pick a date from this selector. The database now consists of short periods of time (1-2hrs) between "+str(dates_min_max['min'][0])+" and "+str(dates_min_max['max'][0])+". More coming soon."))


postgres_select_query = """ SELECT * FROM public.space_stations WHERE date(date_time) = '"""+day_selection+"'"
cursor.execute(postgres_select_query)

# reading our query into pandas dataframe
data_frame = sqlio.read_sql_query(postgres_select_query, connection)
data_frame = data_frame.drop(['date_time', 'id','station'], axis=1)
data_frame['lat'] = pd.to_numeric(data_frame.lat)
data_frame['lon'] = pd.to_numeric(data_frame.lon)

st.map(data_frame)

row3_1, row3_2 = st.beta_columns((1,1))

with row3_1:
    st.title("Potential to-do next with this app:")
    st.write("""
    ★ Additional data collection: Create orchestration for repeated data collection. (https://deckgl.readthedocs.io/en/latest/gallery/icon_layer.html)\n
    ★ Make the dataset thinner to save space for more days. Postgres is currently hosted on Heroku with max. 10000 rows.\n
    ★ Change dots on first map to icons. Just to look cuter.\n
    ★ Distinguish traces of the two stations by colour on the second map.
    """)

with row3_2:
    st.title("About me")
    st.markdown('Happy Data Analyst working on Engineering skills as we speak. LinkedIn here: https://www.linkedin.com/in/barboraspacilova/' )

