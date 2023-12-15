"""
Example 1: Obtain downsampled RT5 data.
"""
import pandas as pd
import matplotlib.pyplot as plt

from pyeuv.EUVDashboard.clients import UserLANClient

if __name__ == '__main__':
    # Create the client instance, this will invoke a password prompt.
    c = UserLANClient()

    # Get data. The signal name is the same as the one used in Grafana
    # Note that by adding the .1h.mean we downsample the data to an hourly mean.
    df = c.get_signals(
        signals=['s38441.RT05.BDenergyAvgOn.1h.mean'],
        from_time=pd.Timestamp('2018-02-01'),
        to_time=pd.Timestamp('2018-02-10')
    )

    df.columns = ['BDenergyAvgOn']  # Set convenient column name

    # That's it, let's plot the data to see if it worked.
    plt.plot(df.index, df['BDenergyAvgOn'], '.r')
    plt.show()

