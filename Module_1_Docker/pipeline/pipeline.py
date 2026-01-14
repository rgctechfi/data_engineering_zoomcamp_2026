# %%
'''
Command: 'c:/Users/RuruA/Documents/MEGASyncPC/Administratifs/LEARNING/IT/Data_Engineering_Zoomcamp_2026/data_engineering_zoomcamp_2026/.venv/Scripts/python.exe -m pip install ipykernel -U --force-reinstall
import os
os._exit(00)

from ipylab import JupyterFrontEnd
app = JupyterFrontEnd()
app.commands.execute('kernelmenu:restart')

'''
# %% Import

import sys
import pandas as pd

# %%
print("arguments", sys.argv)
day = int(sys.argv[1])
print(f"Running pipeline for day {day}")
# %% Pandas
df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
print(df.head())

df.to_parquet(f"output_day_{sys.argv[1]}.parquet")
# %% Restart kernel

# %%
