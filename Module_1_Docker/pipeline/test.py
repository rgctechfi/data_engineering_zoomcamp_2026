#if crash freeze for interactive python
'''
Command: uv pip install ipykernel -U --force-reinstall
import os
os._exit(00)

from ipylab import JupyterFrontEnd
app = JupyterFrontEnd()
app.commands.execute('kernelmenu:restart')

'''
# Import dependancies

import sys
import pandas as pd

# Get the day
print("arguments", sys.argv)
day = int(sys.argv[1])
print(f"Running pipeline for day {day}")

# Dataframe
df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
print(df.head())

# Export to parquet
df.to_parquet(f"output_day_{sys.argv[1]}.parquet")

# %%
from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')


# %%
