

import os
import pathlib
import sys
# from urllib import parse
from xml.dom.minidom import getDOMImplementation, parse
import numpy as np
import pandas as pd


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation, parse
    xmlns = 'http://www.topografix.com/GPX/1/0'
    
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.10f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.10f' % (pt['lon']))
        time = doc.createElement('time')
        time.appendChild(doc.createTextNode(pt['datetime'].strftime("%Y-%m-%dT%H:%M:%SZ")))
        trkpt.appendChild(time)
        trkseg.appendChild(trkpt)

    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)

    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)

    doc.documentElement.setAttribute('xmlns', xmlns)

    with open(output_filename, 'w') as fh:
        fh.write(doc.toprettyxml(indent='  '))


def get_data(input_gpx):
    # TODO: you may use your code from exercise 3 here.
    #pass

    #idk abt the loop thing here. e3 said it was fine to use a loop. but now it says its only the offset loop allowed. so i am not sure what is explicitly allowd. i am just reusing my code here with slight changes.
    
    doc = parse( str(input_gpx) )
    points = [ ]
    for trkpt in doc.getElementsByTagNameNS('http://www.topografix.com/GPX/1/0', 'trkpt'):
        lat = float( trkpt.getAttribute('lat' ) )
        lon = float( trkpt.getAttribute('lon') )
        time_str = trkpt.getElementsByTagNameNS('http://www.topografix.com/GPX/1/0', 'time' )[0].firstChild.nodeValue
        points.append({ 'datetime': time_str, 'lat': lat, 'lon': lon})
    data = pd.DataFrame(points )
    data[ 'datetime' ] = pd.to_datetime( data[ 'datetime'], utc=True, format='ISO8601')
    return data


def main():
    input_directory = pathlib.Path(sys.argv[1])
    output_directory = pathlib.Path(sys.argv[2])
    
    accl = pd.read_json(input_directory / 'accl.ndjson.gz', lines=True, convert_dates=['timestamp'])[['timestamp', 'x']]
    gps = get_data(input_directory / 'gopro.gpx')
    phone = pd.read_csv(input_directory / 'phone.csv.gz')[['time', 'gFx', 'Bx', 'By']]

    first_time = accl['timestamp'].min()
    
    # TODO: create "combined" as described in the exercise
    
    accl[ 'timestamp'] = accl[ 'timestamp'].dt.round('4s')
    accl = accl.groupby( 'timestamp' ).mean(numeric_only=True)
    
    gps[ 'datetime'] = gps[ 'datetime'].dt.round('4s')
    gps = gps.groupby( 'datetime' ).mean(numeric_only=True)

    best_offset = 0.0
    best_corr = -np.inf

    for offset in np.linspace(-5.0, 5.0, 101):
        phonet = phone.copy()

        phonet['timestamp'] = first_time + pd.to_timedelta(phonet['time'] + offset, unit='sec')
        phonet['timestamp'] = phonet['timestamp'].dt.round('4s')
        phone_grped = phonet.groupby('timestamp').mean(numeric_only=True)

        temp = accl.join(phone_grped, how='inner')
        corr = (temp['x']* temp['gFx']).sum()

        if corr> best_corr:
            best_corr = corr
            best_offset = offset

    phone['timestamp'] = first_time + pd.to_timedelta(phone['time'] + best_offset, unit='sec')
    phone['timestamp'] = phone['timestamp'].dt.round('4s')
    phone = phone.groupby('timestamp').mean(numeric_only=True)
    combined = accl.join(phone, how='inner').join(gps, how='inner')
    combined = combined.reset_index().rename(columns={'timestamp': 'datetime'})


    print(f'Best time offset: {best_offset:.1f}')
    os.makedirs(output_directory, exist_ok=True)
    output_gpx(combined[['datetime', 'lat', 'lon']], output_directory / 'walk.gpx')
    combined[['datetime', 'Bx', 'By']].to_csv(output_directory / 'walk.csv', index=False)


main()
