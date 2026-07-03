import sys
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

filename_1 = sys.argv[1]
filename_2 = sys.argv[2]

data1 = pd.read_csv(filename_1, sep=' ', header= None, index_col=1, 
                  names = ['language', 'page', 'views', 'bytes'])

data2 = pd.read_csv(filename_2, sep=' ', header= None, index_col=1, 
                  names = ['language', 'page', 'views', 'bytes'])

# print(data1.head())
# print(data2.head())

s_views = data1['views'].sort_values(ascending=False)

views = pd.DataFrame()

views['h1'] = data1['views']
views['h2'] = data2['views']



plt.figure(figsize=(10,5))

plt.subplot(1,2,1)

plt.plot(s_views.values)

plt.title("popularity distribution")
plt.xlabel("rank")
plt.ylabel("views")

# plt.show()

plt.subplot(1,2,2)
plt.plot(views['h1'], views['h2'], 'b.')
plt.xscale('log')
plt.yscale('log')
plt.title("popularity correlation")
plt.xlabel("views in hour 1")
plt.ylabel("views in hour 2")
# plt.show()

plt.savefig('wikipedia.png')

