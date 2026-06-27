import time
import numpy as np
import pandas as pd
from implementations import all_implementations


ARRAY = 30000
N = 48

result = []

for _ in range(N):
    random_array = np.random.randint(0, 1000000, size=ARRAY)

    for sort in all_implementations:
        st = time.time()
        res = sort(random_array)
        en = time.time()

        result.append({
            "sort": sort.__name__,
            "time": en - st,
        })

data = pd.DataFrame(result)
data.to_csv('data.csv', index=False)