import requests
import json
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data_df = pd.read_csv('data_deaths.csv')

# Store of all temperatures that caused a death
temps = []

for index, row in data_df.iterrows():
    # Start date of recorded data
    d = datetime.date(2020, 1, 22)

    # Location (used only for debugging)
    location = row["Country/Region"]
    if not pd.isnull(row["Province/State"]):
        location += " " + row["Province/State"]
    print(location)

    # Coordinates at location
    cords = str(row["Lat"]) + \
        ","+str(row["Long"])

    deathcount_total = 0

    # iterates from Jan 22nd to March 22nd
    for i in range(0, 60):

        strdate = str(d.month) + "/" + str(d.day) + "/" + "20"

        # gets deathcount on date
        deathcount = row[strdate]

        new_deaths = deathcount-deathcount_total

        # checks if there was an increase in deaths
        if (new_deaths) < 1:
            d = d+datetime.timedelta(days=1)
            continue

        # finds the date of infection
        d_infection = d-datetime.timedelta(days=15)

        # finds the temperature low at the given coordinates on the date of infection
        unixtime = time.mktime(d_infection.timetuple())
        response_weather = requests.get(
            "https://api.darksky.net/forecast/e2250d5bc97d1b8e39223aa95235d995/"+cords+","+str(int(unixtime))+"?exclude=currently,flags")
        data_weather = response_weather.json()

        # Adds temperature to temps array for every death
        temps.extend([data_weather["daily"]["data"][0]
                      ["temperatureLow"]]*new_deaths)

        # Sets the total deaths new death count
        deathcount_total = deathcount

        # increments date
        d = d+datetime.timedelta(days=1)

# Since data from March 22nd onwards is stored in a different format
# The following function calculates the deaths from March 23nd to March 29th
d = datetime.date(2020, 3, 22)

for i in range(0, 7):
    # Reads data for current day
    srtdate = d.strftime("%m-%d-%Y")
    today_df = pd.read_csv(
        "data_daily/"+srtdate+".csv")
    today_df = today_df[["Deaths", "Combined_Key", "Lat", "Long_"]]

    # Elimates data without coordinates (e.g. Cruise Ships)
    today_df = today_df[today_df.Lat != 0]

    d = d+datetime.timedelta(days=1)

    # Stores data for the next day
    srtdate = d.strftime("%m-%d-%Y")
    tommorow_df = pd.read_csv(
        "data_daily/"+srtdate+".csv")
    tommorow_df = tommorow_df[["Deaths", "Combined_Key", "Lat", "Long_"]]
    tommorow_df = tommorow_df[tommorow_df.Lat != 0]

    # Combines dataframes
    merge_df = tommorow_df.merge(today_df, on='Combined_Key',
                                 how='left', suffixes=('_1', '_2'))

    # Clean Up
    merge_df = merge_df.fillna(0)
    merge_df = merge_df[merge_df.Lat_1 != 0]
    merge_df = merge_df[merge_df.Lat_2 != 0]

    # Calculates change in deaths
    merge_df["Deaths"] = merge_df["Deaths_1"] - merge_df["Deaths_2"]

    # Iterates through every location
    for index, row in merge_df.iterrows():

        cords = str(row["Lat_1"]) + \
            ","+str(row["Long__1"])

        # Finds the date 15 days prior to the infection
        d_infection = d-datetime.timedelta(days=15)
        unixtime = time.mktime(d_infection.timetuple())

        # Skips if there hasnt been a death
        if int(row["Deaths"]) == 0:
            continue

        # Finds the temperature low at cords on d_infection
        response_weather = requests.get(
            "https://api.darksky.net/forecast/e2250d5bc97d1b8e39223aa95235d995/"+cords+","+str(int(unixtime))+"?exclude=currently,flags")
        data_weather = response_weather.json()
        temps.extend([data_weather["daily"]["data"][0]
                      ["temperatureLow"]]*int(row["Deaths"]))


# Converts Temperature to Celcius
temps = [x - 32 for x in temps]
temps = [x * (5/9) for x in temps]

# Plots Graph
plt.hist(temps, bins=np.arange(-20, 30, 2))
plt.xticks(np.arange(-20, 30, 2))
plt.title('Effect of Temperature on Deaths due to Corona Virus')
plt.xlabel('Temperature 15 days before death')
plt.ylabel('Deaths')

plt.show()
