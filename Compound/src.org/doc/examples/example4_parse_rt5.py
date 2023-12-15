"""
How to parse a dat file containing RT5 data
"""

import matplotlib.pyplot as plt

from pyeuv.Parsers import dat_parser

if __name__ == '__main__':
    # Provide  the list of filenames to process
    filenames = ['RT5_test.xz']

    # Choose the signals you want to extract. If you dont' know which signals
    # are available in the file, use dat_parser.ls_dat().
    signal_list = ['BDenergyAvgOn']
    df = dat_parser.parse_dat(filenames, signal_list)

    plt.plot(df.index, df['BDenergyAvgOn'])
    plt.show()
