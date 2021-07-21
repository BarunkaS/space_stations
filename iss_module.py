# These are all functions used in the space station tracking project
# contains functions for both data collection and user output
import json
import urllib.request
from datetime import datetime
import geocoder
import turtle

def opening_url(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read()) 

def station_info(opened_source):
    ss_location = opened_source["positions"]
    ss_lat = float(ss_location[0]["satlatitude"])
    ss_lon = float(ss_location[0]["satlongitude"])
    time_now = str(datetime.utcfromtimestamp(ss_location[0]["timestamp"]).strftime('%Y-%m-%d %H:%M:%S'))
    ss_name = opened_source["info"]["satname"]
    return time_now, 1, ss_name, ss_lat, ss_lon 

def my_position():
    return str(geocoder.ip('me').latlng)

def create_turtle_object(gif_file):
    turtle_object = turtle.Turtle()
    turtle_object.shape(gif_file)
    turtle_object.setheading(45)
    turtle_object.penup()
    return turtle_object
