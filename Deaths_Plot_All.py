import requests
import json
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data_df = pd.read_csv('./Data/data_deaths.csv')

# Store of all temperatures that caused a death
temps = []
countries = []
locations = []
humidities = []
dewpoints = []
temperatureHighs = []
uvIndexes = []


for index, row in data_df.iterrows():
    # Start date of recorded data
    d = datetime.date(2020, 1, 22)

    # Location
    location = row["Country/Region"]
    if not pd.isnull(row["Province/State"]):
        location += " " + row["Province/State"]
    print(location)

    # Coordinates at location
    cords = str(row["Lat"]) + \
        ","+str(row["Long"])

    deathcount_total = 0

    # iterates from Jan 22nd to March 22nd
    for i in range(0, 67):

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
        # other potential variables of interest
        humidities.extend([data_weather["daily"]["data"][0]
                           ["humidity"]]*new_deaths)

        dewpoints.extend([data_weather["daily"]["data"][0]
                          ["dewPoint"]]*new_deaths)

        temperatureHighs.extend([data_weather["daily"]["data"][0]
                                 ["temperatureHigh"]]*new_deaths)

        uvIndexes.extend([data_weather["daily"]["data"][0]
                          ["uvIndex"]]*new_deaths)

        # Stores Location
        countries.extend([row["Country/Region"]]*new_deaths)
        locations.extend([location]*new_deaths)

        # Sets the total deaths new death count
        deathcount_total = deathcount

        # increments date
        d = d+datetime.timedelta(days=1)


data_df = pd.read_csv('./Data/data_deaths_us.csv')

for index, row in data_df.iterrows():
    # Start date of recorded data
    d = datetime.date(2020, 1, 22)

    if row["Admin2"] == "Unassigned":
        continue

    # Location
    location = row["Country_Region"] + " " + row["Province_State"]

    print(location)

    # Coordinates at location
    cords = str(row["Lat"]) + \
        ","+str(row["Long_"])

    deathcount_total = 0

    # iterates from Jan 22nd to March 22nd
    for i in range(0, 67):

        strdate = str(d.month) + "/" + str(d.day) + "/" + "20"

        if strdate == "3/22/20":
            continue

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

        # other potential variables of interest
        humidities.extend([data_weather["daily"]["data"][0]
                           ["humidity"]]*new_deaths)

        dewpoints.extend([data_weather["daily"]["data"][0]
                          ["dewPoint"]]*new_deaths)

        temperatureHighs.extend([data_weather["daily"]["data"][0]
                                 ["temperatureHigh"]]*new_deaths)

        uvIndexes.extend([data_weather["daily"]["data"][0]
                          ["uvIndex"]]*new_deaths)

        # Stores Location
        countries.extend([row["Country_Region"]]*new_deaths)
        locations.extend([location]*new_deaths)

        # Sets the total deaths new death count
        deathcount_total = deathcount

        # increments date
        d = d+datetime.timedelta(days=1)


# Converts Temperature to Celcius
temps = [x - 32 for x in temps]
temps = [x * (5/9) for x in temps]

temperatureHighs = [x - 32 for x in temperatureHighs]
temperatureHighs = [x * (5/9) for x in temperatureHighs]

tempsavg = [(a+b)/2 for a, b in zip(temperatureHighs, temps)]

# csv export
csv = {'Country': countries,
       'Temperature Low': temps,
       'Country & Province': locations,
       'Humidity': humidities,
       'Dew Point': dewpoints,
       'Temperature High': temperatureHighs,
       'Temperature Avg': tempsavg,
       'Uv Index': uvIndexes
       }

df = pd.DataFrame(
    csv, columns=['Country', 'Temperature Low', 'Country & Province', 'Humidity', 'Dew Point', 'Temperature High', 'Uv Index'])

df.to_csv('./Output/deaths_all.csv', index=False, header=True)

plt.rcParams['axes.axisbelow'] = True
plt.hist(temps, bins=np.arange(-20, 30, 2), edgecolor="black",
         linewidth='1.5', facecolor='red', alpha=0.9)
plt.xticks(np.arange(-20, 30, 4))
plt.title('Effect of Temperature on Deaths due to Corona Virus')
plt.xlabel('Temperature Low 15 days before death')
plt.ylabel('Deaths')
plt.grid(linestyle=':')
plt.savefig('./Output/Death_Plot.png'', bbox_inches='tight')

plt.show()

print(df)
