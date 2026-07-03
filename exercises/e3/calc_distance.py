import sys
import numpy as np
import pandas as pd
from pykalman import KalmanFilter
from xml.dom.minidom import parse



def get_data( gpx_filename ):
    doc = parse( gpx_filename )
    points = [ ]
    for trkpt in doc.getElementsByTagNameNS('http://www.topografix.com/GPX/1/0', 'trkpt'):
        lat = float( trkpt.getAttribute('lat' ) )
        lon = float( trkpt.getAttribute('lon') )
        time_str = trkpt.getElementsByTagNameNS('http://www.topografix.com/GPX/1/0', 'time' )[0].firstChild.nodeValue
        points.append({ 'datetime': time_str, 'lat': lat, 'lon': lon})
    data = pd.DataFrame(points )
    data[ 'datetime' ] = pd.to_datetime( data[ 'datetime'], utc=True)
    return data

def distance(points):
    #  formula from: https://en.wikipedia.org/wiki/Haversine_formula
    lat = np.radians( points['lat'].values)
    lon = np.radians( points['lon'].values)
    
    dlat = lat[1:] - lat[:-1]
    dlon = lon[1:] - lon[:-1]
    
    a = np.sin( dlat/2)**2 + np.cos(lat[:-1]) * np.cos( lat[1:]) * np.sin(dlon/2)**2
    c = 2 * np.arcsin( np.sqrt(a))
    r = 6371000
    return np.sum(r * c)

# points = pd.DataFrame({'lat': [49.28, 49.26, 49.26], 'lon': [123.00, 123.10, 123.05]})
# print(distance(points).round(6))

def smooth(points):
    initial_state = points[['lat', 'lon', 'Bx', 'By']].iloc[0].values
    
    obs_std = 5e-5
    observation_covariance = np.diag([obs_std, obs_std, 2, 2]) ** 2
    
    transition_covariance = np.diag([obs_std/5, obs_std/5, 2, 2]) ** 2
    
    transition = [
        [1, 0,5e-7,34e-7],[0, 1,-49e-7,9e-7],[0, 0,  1,0],[0, 0, 0, 1]]
    
    kf = KalmanFilter(initial_state_mean=initial_state,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance,
        transition_matrices=transition)
    
    kalman_data = points[ [ 'lat', 'lon', 'Bx', 'By' ] ]
    smoothed, _ = kf.smooth( kalman_data ) 
    
    smoothed_points = points.copy()
    smoothed_points[ 'lat' ] = smoothed[:,0 ]  
    smoothed_points['lon' ] = smoothed[:, 1 ] 
    return smoothed_points


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.7f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.7f' % (pt['lon']))
        trkseg.appendChild(trkpt)
    
    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)
    
    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)
    
    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent=' ')


def main():
    input_gpx = sys.argv[1]
    input_csv = sys.argv[2]
    
    points = get_data(input_gpx).set_index('datetime')
    sensor_data = pd.read_csv( input_csv,parse_dates=[ 'datetime'] ).set_index('datetime' )
    points['Bx' ] = sensor_data['Bx']
    points['By'] = sensor_data[ 'By' ]

    dist = distance(points)
    print(f'Unfiltered distance: {dist:.2f}')

    smoothed_points = smooth(points)
    smoothed_dist = distance(smoothed_points)
    print(f'Filtered distance: {smoothed_dist:.2f}')

    output_gpx(smoothed_points, 'out.gpx')


if __name__ == '__main__':
    main()
