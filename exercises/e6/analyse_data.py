import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import numpy as np


data = pd.read_csv('data.csv')

means = data.groupby('sort')['time'].mean().sort_values()
print("mean times per sort implementation: ")
print(means.to_string()) 

groups = data.groupby('sort')['time'].apply(np.array)

f, p = stats.f_oneway(*groups.values)
print("oneway ANOVA: ")
print(f"f: {f:.4g}, p: {p:.4g}")

tukey = pairwise_tukeyhsd(data['time'], data['sort'])
print("tukey")
print(tukey)

