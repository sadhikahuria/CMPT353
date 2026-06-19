import sys

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


def distance(city, stations):
    lt = np.radians(city['latitude'])
    ln = np.radians(city['longitude'])
    lt2 = np.radians(stations['latitude'].values)
    ln2 = np.radians(stations['longitude'].values)

    dlt = lt2 - lt
    dln = ln2 - ln

    a = np.sin( dlt/2)**2 + np.cos(lt) * np.cos( lt2) * np.sin( dln/2)**2
    c = 2 * np.arcsin( np.sqrt(a))


    return 6371000 * c
    
    # return 0



def best_tmax(city, stations):
    d = distance(city, stations)
    idx = d.argmin()
    return stations.iloc[idx]['avg_tmax']
    # return 0


def main():
    stationsFile = sys.argv[1]
    citiesFile = sys.argv[2]
    outputFile = sys.argv[3]

    stations = pd.read_json(stationsFile, lines=True)
    stations['avg_tmax'] = stations['avg_tmax'] / 10

    cities = pd.read_csv(citiesFile)
    cities = cities.dropna(subset=['population', 'area'])
    cities['area'] = cities['area'] / 1000000
    cities = cities[cities['area'] <= 10000]
    
    cities['density'] = cities['population'] / cities['area']
    cities['avg_tmax'] = cities.apply(best_tmax, axis=1, stations=stations)


    

    plt.figure()
    plt.scatter(cities['avg_tmax'], cities['density'], alpha=0.5)
    plt.xlabel('Avg Max Temperature (\u00b0C)')
    plt.ylabel('Population Density (people/km\u00b2)')

    plt.savefig(outputFile)



main()

