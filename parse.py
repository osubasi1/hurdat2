import pandas as pd
from datetime import datetime
import requests
import geopandas as gpd
from shapely.geometry import Point

"""
Using a programming language of your choice, build an application to parse the HURDAT2 loc_data, identify
the storms that made landfall in Florida, and output a report listing the name, date of landfall, and max
wind speed for each event.

Your code should be well commented and organized so other programmers can understand how it
works. During your interview, be prepared to walk through the code, discuss your design choices, and
take notes on any feedback. After the interview, you will have the opportunity to take the same project
further and incorporate feedback from the interview to expand your solution.

***Note that there is a Landfall indicator in the track loc_data, but see if you can find a way to identify 
landfalling events without using that indicator.

landfall: the land that is first seen or reached after a journey by sea or air
"""

"""
A method that converts strings from NHC to float locations. It takes a string as argument and multiply it by either
1 or -1 and return float value of this multiplication. 
"""


def lat_lon_to_float(value):
    # If the last character of string is S or W then we will multiply it by -1
    if (value[-1] == 'S') or (value[-1] == 'W'):
        multiplier = -1
    # if it is E or N then multiply by 1
    else:
        multiplier = 1
    # return the float value (except the last char) because what we read from file is string
    return float(value[:-1]) * multiplier


"""
A method that takes a url as an argument and sends HTTP requests to get the txt file.
 Then parse that file and store the necessary data to a dataframe and it returns that dataframe.
"""


def getAllAsDataframe(url):

    data = []   # Empty list that is going to hold the data
    response = requests.get(url)    # send a request to given url to get the raw data
    raw_file = response.text
    # Iterate line by line to get data
    for line in raw_file.splitlines():
        if line.startswith('AL'):  # if it starts with AL then it is a header line
            storm_id = line.split(',')  # split it by comma
            # with strip we will get rid of all the white spaces
            storm_number = storm_id[0].strip()
            storm_name = storm_id[1].strip()
        # if it is not header line then it is loc_data that proceed this header
        else:
            location_line = line.split(',')
            # use datetime library to store date and time in given format
            dt = datetime.strptime(location_line[0] + location_line[1], '%Y%m%d %H%M')
            record_identifier = location_line[2].strip()
            storm_status = location_line[3].strip()
            storm_lat = lat_lon_to_float(location_line[4].strip())
            storm_lon = lat_lon_to_float(location_line[5].strip())
            max_speed = float(location_line[6].strip())
            data.append(
                [storm_number, storm_name, storm_status, record_identifier, storm_lat, storm_lon, dt, max_speed])

    df = pd.DataFrame(data,
                      columns=['Storm Number', 'Storm Name', 'Storm Status', 'Storm Identifier', 'Lat', 'Lon', 'Time',
                               'Max Speed'])
    return df

"""
A method that takes a dataframe, which has all the data in the text file, as an argument and iterate over these data 
to find locations that are in Florida and return a new dataframe that has name, date, and max wind speed.
"""


def getFloridaData(df):

    # This is a data that I found on the internet and it has the US map but I use florida part to pinpoint if event
    # happened in Florida.
    states = gpd.read_file('data/location_data/loc_data/usa-states-census-2014.shp')
    floridaGeometry = states[states["NAME"] == "Florida"]
    polygonFlorida = floridaGeometry.geometry

    data = []   # Empty list that is going to hold the required data (name, date and max wind)
    removeRedundant = []    # Another empty list to keep track of unique storms
    # Iterate through dataframe and get all the required data
    for ind in df.index:
        # Use Point from shapely.geometry to create a point for each event from lon and lat
        point = Point((df['Lon'][ind], df['Lat'][ind]))
        # Check if the point is in Florida
        if (polygonFlorida.intersects(point).bool()) & (df['Storm Status'][ind] == 'HU'):
            # name, date of landfall, and max wind speed for each event
            name = df['Storm Name'][ind]
            dt = df['Time'][ind]
            maxWind = df['Max Speed'][ind]
            if name not in removeRedundant:
                removeRedundant.append(name)
                data.append([name, dt, maxWind])

    requiredDataframe = pd.DataFrame(data, columns=['Storm Name', 'Time', 'Max Speed'])
    return requiredDataframe


def main():
    url = 'https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2021-041922.txt'
    df = getAllAsDataframe(url)
    florida_df = getFloridaData(df)
    # Printing all the loc_data in the df2 dataframe
    with pd.option_context('display.max_rows', None,  # display.max_rows and display.max_columns default value is 10
                           'display.max_columns', None,  # but setting it to none will display everything
                           'display.precision', 3,
                           # indicates that after decimal point shows up to 3 values this also does
                           # not affect this since we have only one after decimal.
                           ):
        print(florida_df)


main()
