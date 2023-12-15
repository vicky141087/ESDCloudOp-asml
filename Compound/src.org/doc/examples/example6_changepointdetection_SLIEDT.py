''''
How to download, process and yield change points from SLIEDT data
PART 1: Download SLIEDT data from influx (custom script but you can tweak / use what you want). For now it only takes the last collector
PART 2: Put the x (Gp) and y (SLIE/DT) data in change point detection function to generate the changepoints
PART 3: (Optional) put the output file from change point detection function through the plotter to get graphical information
'''''


## ---- PART 1: Download data from influx ----
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from scipy.fftpack import fft, fftfreq, fftshift
from scipy.signal import butter, filtfilt, freqz

from pyeuv.EUVDashboard.clients import UserLANClient
c = UserLANClient()

from pyeuv.Collector.Shared.directory_structure import get_machine_directory, get_luer_directory, get_collector_directory, get_share_base_directory
import pyeuv.Collector.Shared.directory_structure as directory_structure
from pyeuv.Shared.configuration import Configuration
conf = Configuration()

if __name__ == '__main__':

    machine_list = c.get_machine_list()
    machine_name = []  # List with machine_names only
    for i in range(len(machine_list)):
        machine_name.append(machine_list[i]['displayname'])
    machine_name.sort()

    selected_mname = ''
    # Automatically load from pyeuv dashboard SDDA?
    main = Tk()
    main.title("Select machine names")
    main.geometry("350x200")

    combo = Combobox(main)
    combo['values'] = machine_name
    combo.current(1)
    combo.grid(column=0, row=0)


    def clicked():
        global selected_mname
        selected_mname = combo.get()
        print(selected_mname)
        main.destroy()
        # return selected_mname


    btn = ttk.Button(main, text="Submit", command=clicked)
    btn.grid(column=0, row=2)

    main.mainloop()


    def get_source_nr(machine_name):
        for m in machine_list:
            if m['displayname'] == machine_name:
                return m['source_nr']


    source_nr = 's' + str(get_source_nr(selected_mname))
    # source_nr = 's62294'

    last_collector = True
    specific_machine = selected_mname
    base_dir = get_share_base_directory()
    machine_list = c.get_machine_list(return_type='dataframe')
    # currentMachines = machine_list[(machine_list.replacement_vessel == "") | (machine_list.replacement_vessel.isnull())]
    machines = machine_list  # [currentMachines['hardware'] == '3400']
    if specific_machine is not None: machines = machines.loc[machines.displayname == specific_machine]

    for index, item in machines.iterrows():
        machine = machines[machines.index == index]

        item_new = pd.DataFrame(columns=list(item.index))
        item_new.loc[0] = list(item.values)

        conf.set_configuration(c, item_new)
        collectors = conf.get_collectors(c, conf.source_id)

        if len(collectors) == 0:
            print('no collectors for {}', format(conf.machine_name))
            continue
        if last_collector:
            tail = 1
        else:
            tail = 666
        for i, collector in collectors.tail(tail).iterrows():
            conf.set_configuration(c, item_new, collector.swap)
            print('{} | {} ({})'.format(conf.machine_name, conf.collector_name, pd.Timestamp('now')))
            collector_directory = get_collector_directory(conf, base_dir)
            radon_dir = get_luer_directory(collector_directory)

    tstart = pd.Timestamp(conf.start_time)
    tstop = pd.Timestamp(conf.end_time)

    y = c.get_signals(
        ['{0}.Collector._SLIE_DT_Norm'.format(source_nr)],
        from_time=tstart, to_time=tstop
    )
    y.columns = ['y']
    # Load x signal; in this case pulserate in Gp
    x = c.get_signals(
        ['{0}.Collector._PulseCount'.format(source_nr)],
        from_time=tstart, to_time=tstop
    ) * 1e-9  # To Gp
    x.columns = ['x']
    # Interpolate x to match length of y
    if x.shape != y.shape:
        xn = y
        xn['xx'] = np.interp(
            y['y'].index.astype('int64'),
            x['x'].index.astype('int64'),
            x['x'].values
        )
        x = xn
    # Make np array with only values
    y = y.values[:, 0]
    x = x.values[:, 1]

    ## --- PART 2: Calculate changepoints ----

    data_cpd = calculate_changepoints(x, y, Ts=0.1, Tc=5, order=6, cp_mag=0.2, limits=[-0.6, -0.3, 0])

    ## ---- PART 3: Plot the calculated changepoints and  ----

    plot_changepoints(data_cpd)


