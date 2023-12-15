import pandas as pd
from pyeuv.EUVDashboard.clients import UserLANClient

if __name__ == '__main__':

    # Create the client object
    c = UserLANClient()

    # Define time window to get the data for
    tstart = pd.Timestamp('2018-09-01 00:00:00')
    tstop = pd.Timestamp('2018-09-05 00:00:00')

    # Retrive a single field using []
    data = c.get_signals(
        ["s62269.SourceLog.OSD-0200[target_euv]"],
        pd.Timestamp('2018-09-01 14:00:00'),
        pd.Timestamp('2018-09-05 15:00:00')
    )
    print(data.head(5))

    # Retrieve all fields using the [*]
    data = c.get_signals(
        ["s62269.SourceLog.OSD-0200[*]"],
        pd.Timestamp('2018-09-01 14:00:00'),
        pd.Timestamp('2018-09-05 15:00:00')
    )

    print(data.head(5))