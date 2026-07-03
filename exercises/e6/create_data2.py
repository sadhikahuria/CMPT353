import pandas as pd
import numpy as np
import time
from implementations import all_implementations

array = np.random.rand(10)
result = []
for test in range(50):
    array = np.random.randint(0,100000, size= 70000)
    for sort in all_implementations:
        st = time.time()
        sort(array)
        en = time.time()
        elapsed = st-en
        result.append([sort.__name__, en-st])

data = pd.DataFrame(result, columns = ["sort","time"])
data.to_csv("data.csv", index=False)
    