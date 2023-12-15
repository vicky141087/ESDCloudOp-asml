"""
How to download DW_SLIE from PMA NG for machine m9445
"""

import pandas as pd
import matplotlib.pyplot as plt

from pyeuv.PMA.clients import PMAClient


# PMA credentials and api_key. Please refer to example #5 in the documentation for more info.
username = "<your_pma_username>"

# Warning: This is for testing only. Do not store passwords in your code.
password = "<your_pma_password>"
api_key = "<your_pma_api_key>"

machine = {
    'machine_nr': 9445,
    'name': 'TSMC 7'
}

# Download the data
pma_client = PMAClient(username, password, api_key)
df_slie = pma_client.get_parameters(['DW_SLIE'], machine, pd.Timestamp('2019-04-01'),
                                    pd.Timestamp('2019-05-01'), verbose=True)['DW_SLIE']

# Plot the results
plt.plot(df_slie.index, df_slie['value'], '.r')
plt.show()
