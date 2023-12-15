# This Python file uses encoding: utf-8

"""
POB TMONI - Projection Optics Box Transmission Monitoring tool

This file only contains examples for how to call/execute the POB_TMONI code.
As such all code is put behind if statements to prevent execution except manually.

Copyright 2020, ASML HOLDING N.V. (INCLUDING AFFILIATES). ALL RIGHTS RESERVED.
"""

# Imports
if __name__ == '__main__':
    # Suppress all the pesky Pandas warnings
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

    import glob
    import os
    import pandas as pd

    from pathlib import Path

    # ASML Libraries
    from pyeuv.EUVDashboard.clients import UserLANClient  # https://euv-dashboard.asml.com/service/tools.html

    import pyeuv.STC.POB.POB_calc as POB  # Do calculations
    import pyeuv.STC.POB.POB_IO as POB_IO  # Get data
    import pyeuv.STC.POB.POB_reporting as plots  # Make plots
    import pyeuv.STC.general.shared as shared

# Get Influx client, note SublimeText users need a workaround for password input
if __name__ == '__main__':
    client = UserLANClient()

# Get machine overview
if __name__ == '__main__':
    # Get machine overview, just for reference
    mach_overview = pd.DataFrame(client.get_machine_list()).rename(
        columns={'machine_nr': 'machine_id'}).sort_values(by=['customer', 'source_nr'])
    mach_overview = mach_overview.loc[mach_overview[
        'machine_id'].str.contains('TMP') == False]  # Filter out TMP machines

# Analyse one machine
if __name__ == '__main__':
    # Set parameters
    source_nr = '62315'
    from_time = pd.Timestamp(year=2013, month=1, day=1).tz_localize('UTC')
    to_time = pd.Timestamp.now().tz_localize('UTC')
    verbose = False

    # Get data, do calculations, make result PPT
    data_dict = POB_IO.get_data(client, source_nr,
                                from_time=from_time,
                                to_time=to_time,
                                verbose=verbose)
    POBclass = POB.POB_TMONI(data_dict, local=True, verbose=verbose)
    POBclass.run()
    ppt = plots.make_ppt_for_one_machine(POBclass)

# Analyse multiple machines
if __name__ == '__main__':
    for i, ituple in enumerate(mach_overview.itertuples()):
        idict = ituple._asdict()

        print(f'{i:2.0f}/{mach_overview.shape[0] - 1:2.0f} - {idict["machine_id"]} / {idict["source_nr"]}')
        from_time = pd.Timestamp(year=2013, month=1, day=1).tz_localize('UTC')
        if idict["machine_id"] == '5786':  # machine_id reused, do not use earlier data
            from_time = pd.Timestamp(year=2017, month=7, day=1).tz_localize('UTC')
        to_time = pd.Timestamp.now().tz_localize('UTC')
        verbose = False

        # Get data, do calculations, make result PPT
        data_dict = POB_IO.get_data(client, idict["source_nr"],
                                    from_time=from_time,
                                    to_time=to_time,
                                    verbose=verbose)
        if not data_dict['FSLIE'].empty:
            POBclass = POB.POB_TMONI(data_dict, local=True, verbose=verbose)
            POBclass.run()
            ppt = plots.make_ppt_for_one_machine(POBclass)

# Combine multiple results for combined plot
if __name__ == '__main__':
    def combine_result_csv_files(searchstring=Path(r'~\.tmoni\result\pob_s*.csv')):
        df = pd.DataFrame()
        results = glob.glob(str(searchstring.expanduser()))
        for res in results:
            dfres = pd.read_csv(res)
            dfres['source_nr'] = str(os.path.split(res)[-1].replace('pob_s', '')[:5])
            df = df.append(dfres)
        del df['machine_id']
        df = df.merge(mach_overview[['source_nr', 'machine_id', 'displayname', 'customer', 'hardware']])
        df = df.merge(df.groupby(['doe_name', 'machine_id', 'source_nr'], as_index=False)[
                      'FSLIE'].count().rename(columns={'FSLIE': 'counter'}).query('counter>=2'), how='inner')

        df_endresult = df.copy().query('doe_name in ["Small Annular", "Large Conventional"]')
        df_endresult = df_endresult.set_index('_ts_index_', drop=False)
        df_endresult = df_endresult.loc[df_endresult.groupby(['doe_name', 'machine_id', 'source_nr'])[
            '_ts_index_'].tail(1).dropna().index]  # Only select latest value
        # Select only most often used pupil of Small Annular and Large Conventional
        df_endresult = shared.merge_ts_index(df_endresult.groupby(['machine_id', 'source_nr'], as_index=False).agg(
            {'pupil_usage_rank': 'min'}), df_endresult, how='left')
        df_endresult = df_endresult.query('FSLIE_cumprod!=1')

        df = df.merge(df_endresult[['machine_id', 'doe_name']], how='inner')

        return df, df_endresult

    df, df_endresult = combine_result_csv_files()
    df_endresult.to_csv(os.path.expanduser(r'~\.tmoni\result\ALL_COMBINED.csv'))

    plots.make_summary_ppt(df, df_endresult, fname=os.path.expanduser(r'~\.tmoni\result\ALL_COMBINED.pptx'))
