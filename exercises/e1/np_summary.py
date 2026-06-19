import numpy as np


data = np.load('monthdata.npz')
totals = data['totals']
counts = data['counts']

print('Row with lowest total precipitation:')
print(np.argmin(totals.sum(axis=1)))

print('Average precipitation in each month:')
print(totals.sum(axis=0) / counts.sum(axis=0))

print('Average precipitation in each city:')
print(totals.sum(axis=1) / counts.sum(axis=1))

print('Quarterly precipitation totals:')
print(totals.reshape(totals.shape[0], 4, 3).sum(axis=2))
