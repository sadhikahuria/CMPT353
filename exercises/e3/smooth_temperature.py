import sys
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
from pykalman import KalmanFilter
import numpy as np



cpu_data = pd.read_csv( sys.argv[1], parse_dates=['timestamp'] )

plt.figure(figsize=(12, 4))
plt.plot( cpu_data['timestamp'],cpu_data['temperature'], 'b.', alpha=0.5, label='Raw' )
loess_smoothed = lowess( cpu_data['temperature'] , cpu_data['timestamp'].astype(np.int64),frac=0.02 )
plt.plot( cpu_data['timestamp'] , loess_smoothed[: ,1] , 'r-',  label='LOESS')

kalman_data = cpu_data[ ['temperature', 'cpu_percent','sys_load_1', 'fan_rpm' ] ]

initial_state = kalman_data.iloc[0].values
observation_covariance = np.diag( [3, 10, 1, 100] ) ** 2
transition_covariance = np.diag( [0.5, 1, 0.5, 10] ) ** 2
transition = [[0.99, 0.5, 0.2, -0.001],[0.1, 0.4, 2.1, 0],[0, 0, 0.95, 0],[0, 0, 0, 1]]

kf = KalmanFilter(initial_state_mean=initial_state,
    observation_covariance=observation_covariance,
    transition_covariance=transition_covariance,
    transition_matrices=transition)

kalman_smoothed, _ = kf.smooth( kalman_data )
plt.plot( cpu_data[ 'timestamp' ], kalman_smoothed[:, 0 ], 'g-', label='Kalman' )

plt.legend()
plt.savefig( 'cpu.svg' )