from datetime import timedelta

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm
from vesninlib.vesninlib import DEFAULT_PARAMS
import matplotlib.dates as mdates

def plot_single_sat(data_plot, sat, epc, plot_product,
                    limits=(3600, 3600),
                    shift=0.5,
                    site_labels=False,
                    namefile='data/result/11.png'):
    i = 0
    plt.figure(figsize=(6, 13))
    plt.rcParams.update(DEFAULT_PARAMS)
    plot_ax = plt.axes()

    sites = list()
    locs = list()
    for d in data_plot[sat]:
        _t = d['time']
        _val = d[plot_product]
        plt.plot(_t, _val + i * shift, marker='.')
        locs.append(i * shift)
        i = i + 1
        plt.axvline(x=epc['time'], color='black', linewidth=3)
        sites.append(d['site'])
    plt.xlim(epc['time'] - timedelta(0, limits[0]),
             epc['time'] + timedelta(0, limits[1]), )
    locs = [-2 * shift, -shift] + locs + [i * shift, (i + 1) * shift]
    sites = [''] * 2 + sites + [''] * 2
    if site_labels:
        plt.yticks(locs, sites)
    plt.ylim(-2 * shift, (i + 1) * shift)
    plot_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.title('Satellite ' + sat)
    plt.grid()
    plt.xlabel('UTC for February 6, 2023')
    plt.savefig(namefile)

def fit_and_plot_distribution(data, xmin=0, xmax=4000, namefile='data/result/10.png'):
    plt.figure(figsize=(18, 9))
    mu, std = norm.fit(data)
    plt.grid()
    # Plot the histogram.
    counts, edges, bars = plt.hist(data, bins=20, density=True, alpha=0.6, color='g')
    # plt.bar_label(bars)
    y = ((1 / (np.sqrt(2 * np.pi) * std)) *
         np.exp(-0.5 * (1 / std * (edges - mu)) ** 2))
    # Plot the PDF.
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)  # * len(data) * len(data)
    plt.plot(x, p, 'k', linewidth=3, color='black')
    title = "Fit results: mean = %.2f m/s,  STD = %.2f m/s" % (mu, std)
    plt.xlabel('velocity, m/s')

    ytick = [i / 10000 * 1.03213 for i in range(0, 13, 2)]
    ylables = [round(i) for i in range(0, 13, 2)]
    plt.yticks(ytick, ylables)
    plt.ylabel('Occuranes')
    plt.title(title)
    plt.ylim(0, 13 / 10000 * 1.03213)
    plt.savefig(namefile)