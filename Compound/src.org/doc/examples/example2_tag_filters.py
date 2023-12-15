import pandas as pd
from pyeuv.EUVDashboard.clients import UserLANClient

if __name__ == '__main__':

    # Create the client object
    c = UserLANClient()

    # Get data. The signal name is the same as the one used in Grafana
    # Note that by adding the {subroutine=MP} part we retrieve only the points
    # where this condition is true. It's possible to add multiple tag filters.
    data = c.get_signals(
        ['s62265.RT23.TFMmajorAxis{subroutine=MP}{in_spec=True}'],
        pd.Timestamp('2018-08-23 14:00:00'),
        pd.Timestamp('2018-08-23 15:00:00')
    )

    print(data)