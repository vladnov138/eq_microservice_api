from datetime import datetime
import matplotlib.pyplot as plt
from datetime import (datetime,
                      timedelta)
from scipy.stats import norm
import matplotlib.dates as mdates
import numpy as np
from earthquakeplotlib import EPICENTERS, retrieve_data_multiple_source, retrieve_data, get_dist_time, \
    plot_distance_time, plot_line, plot_sites, get_sites_coords, select_visible_sats_data, get_visible_sats_names, \
    select_sats_by_params, select_reoder_data, get_dtecs, calculate_distances_from_epicenter, DEFAULT_PARAMS

C_LIMITS = {
    'ROTI': [-0, 0.5, 'TECu/min\n'],
    '2-10 minute TEC variations': [-0.6, 0.6, 'TECu'],
    '10-20 minute TEC variations': [-0.8, 0.8, 'TECu'],
    '20-60 minute TEC variations': [-1.0, 1.0, 'TECu'],
    'tec': [0, 50, 'TECu/min'],
    'tec_adjusted': [0, 50, 'TECu'],
}

eq_location = EPICENTERS['10:24']


def create_first_type():
    data = retrieve_data("data/roti_10_24.h5", "ROTI")
    x, y, c = get_dist_time(data, eq_location)
    plot_distance_time(x, y, c, "ROTI", clims=C_LIMITS, data=data)
    # plot_line(2.000, datetime(2023, 2, 6, 10, 35))
    plt.savefig('data/result/1.png')

    data = retrieve_data("data/dtec_2_10_10_24.h5", "2-10 minute TEC variations")
    x, y, c = get_dist_time(data, eq_location)
    plot_distance_time(x, y, c, "2-10 minute TEC variations", data=data, clims=C_LIMITS)
    # plot_line(1.500, datetime(2023, 2, 6, 10, 32, 30), style='dashed')
    # plot_line(1.300, datetime(2023, 2, 6, 10, 34, 30))
    # plot_line(0.900, datetime(2023, 2, 6, 10, 37), style='dotted')
    plt.savefig('data/result/2.png')


def create_second_type():  # use 2 and more files for create pictures
    data = retrieve_data_multiple_source(["data/roti_10_24.h5", "data/tnpgn_roti_10_24.h5"],
                                         "ROTI")
    x, y, c = get_dist_time(data, eq_location)
    plot_distance_time(x, y, c, "ROTI", data=data)
    # plot_line(2.000, datetime(2023, 2, 6, 10, 35))
    plt.savefig('data/result/4.png')

    data = retrieve_data_multiple_source(["data/dtec_2_10_10_24.h5", "data/tnpgn_dtec_2_10_10_24.h5"],
                                         "2-10 minute TEC variations")
    x, y, c = get_dist_time(data, eq_location)
    plot_distance_time(x, y, c, "2-10 minute TEC variations", data=data)
    # plot_line(1.500, datetime(2023, 2, 6, 10, 32, 30), style='dashed')
    # plot_line(1.300, datetime(2023, 2, 6, 10, 34, 30))
    # plot_line(0.900, datetime(2023, 2, 6, 10, 37), style='dotted')
    plt.savefig('data/result/5.png')

    data = retrieve_data_multiple_source(["data/dtec_10_20_10_24.h5", "data/tnpgn_dtec_10_20_10_24.h5"],
                                         "10-20 minute TEC variations")
    x, y, c = get_dist_time(data, eq_location)
    plot_distance_time(x, y, c, "10-20 minute TEC variations", data=data)
    plt.savefig('data/result/6.png')


def create_third_type():  # dick knows what's going on here, but it seems you can set your own C_LIMITS
    C_LIMITS = {
        'ROTI': [-0, 0.5, 'TECu/min\n'],
        '2-10 minute TEC variations': [-0.6, 0.6, 'TECu'],
        '10-20 minute TEC variations': [-0.4, 0.4, 'TECu'],
        '20-60 minute TEC variations': [-0.6, 0.6, 'TECu'],
        'tec': [0, 50, 'TECu/min'],
        'tec_adjusted': [0, 50, 'TECu'],
    }

    eq_location = EPICENTERS['10:24']

    data = retrieve_data("data/roti_10_24.h5", "ROTI")
    x, y, c = get_dist_time(data, eq_location)
    plot_distance_time(x, y, c, "ROTI", data=data)
    plt.savefig('data/result/7.png')

    C_LIMITS = {
        'ROTI': [0, 0.3, 'TECu/min\n'],
        '2-10 minute TEC variations': [-0.4, 0.4, 'TECu'],
        '10-20 minute TEC variations': [-0.4, 0.4, 'TECu'],
        '20-60 minute TEC variations': [-0.6, 0.6, 'TECu'],
        'tec': [0, 50, 'TECu/min'],
        'tec_adjusted': [0, 50, 'TECu'],
    }

    eq_location = EPICENTERS['01:17']

    data = retrieve_data("data/roti_01_17.h5", "ROTI")
    times = [t for t in data]
    times.sort()
    data = {t: data[t] for t in times[120:]}  # start from 01:00 UT
    x, y, c = get_dist_time(data, eq_location)
    plot_distance_time(x, y, c, "ROTI", data=data)
    plt.savefig('data/result/8.png')


def create_fourth_type(): # simple
    sites = ['mers', 'nico', 'bshm', 'csar', 'mrav', 'nzrt', 'hama',
             'hrmn', 'drag', 'kabr', 'katz', 'zkro', 'tmar', 'ista']
    local_file = 'data/region_2023-02-06.h5'
    sat = 'G17'
    plot_sites(local_file, sat, sites, 'roti')
    plt.savefig('data/result/9.png')


def fit_and_plot_distribution(data, xmin=0, xmax=4000, namefile='data/result/10.png'):
    # use bacause i don't want to reinstal vesninlib!!!!!
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


def create_fifth_type(local_file='data/region_2023-02-06.h5', save_file='data/result/10.png'):
    tcheck = datetime(2023, 2, 6, 10, 38)
    coords = get_sites_coords(local_file, exclude_sites=['guru'])
    sites = [site for site in coords]
    data = select_visible_sats_data(local_file, sites, tcheck=tcheck)
    visible_sats = get_visible_sats_names(data)
    sats_count = select_sats_by_params(data, visible_sats, tcheck)
    _data = select_reoder_data(data, sats_count)

    sats = ['G17', 'G14', 'G24', 'E08']

    for start_time in [datetime(2023, 2, 6, 10, 35, 0) + timedelta(0, 30 * i) for i in range(1)]:
        deltas = list()
        dists = list()
        velocities = list()

        for sat in sats:
            dtecs = get_dtecs(_data, sort_type='max', sat=sat, threshold=0.25, threshold_type='min')
            elat = np.radians(EPICENTERS['10:24']['lat'])
            elon = np.radians(EPICENTERS['10:24']['lon'])
            calculate_distances_from_epicenter(dtecs, coords, sat, elat, elon)
            for data in dtecs[sat]:
                delta = (data['th_time'] - start_time) / timedelta(0, 1)
                if delta == 0.0:
                    continue
                velocity = data['distance'] / delta
                if velocity < 0 or velocity > 4000:
                    continue
                deltas.append(delta)
                dists.append(data['distance'])
                velocities.append(velocity)
        fit_and_plot_distribution(velocities, namefile=save_file)


def plot_single_sat(data_plot, sat, epc, plot_product,  # use bacause i don't want to reinstal vesninlib!!!!!
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


def create_sixth_type(local_file='data/region_2023-02-06.h5', savefile='data/result/11.png'):
    tcheck = datetime(2023, 2, 6, 10, 38)
    coords = get_sites_coords(local_file, exclude_sites=['guru'])
    sites = [site for site in coords]
    data = select_visible_sats_data(local_file, sites, tcheck = tcheck)
    visible_sats = get_visible_sats_names(data)
    sats_count = select_sats_by_params(data, visible_sats, tcheck)
    _data = select_reoder_data(data, sats_count)

    sat='G17'
    dtecs = get_dtecs(_data, sort_type='max', sat=sat, threshold=0.25, threshold_type='min')
    sites = []
    for d in dtecs[sat]:
        sites.append(d['site'])

    plot_single_sat(dtecs, sat, EPICENTERS['10:24'], 'dtec',
                    limits=(0,1200),
                    shift=0.5, site_labels=True, namefile=savefile)


