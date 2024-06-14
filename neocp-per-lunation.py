import datetime
import ephem
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
import data
import moon


plt.rc('font', family='serif')
plt.rcParams['text.usetex'] = False
fs = 24

# update various fontsizes to match
params = {'figure.figsize': (12, 8),
          'legend.fontsize': 0.7 * fs,
          'axes.labelsize': fs,
          'xtick.labelsize': 0.6 * fs,
          'ytick.labelsize': 0.6 * fs,
          'axes.linewidth': 1.1,
          'xtick.major.size': 7,
          'xtick.minor.size': 4,
          'ytick.major.size': 7,
          'ytick.minor.size': 4}
plt.rcParams.update(params)


def get_phase_on_day(year, month, day):
    try:
        date = ephem.Date(datetime.date(year,month,day))
    except:
        date = ephem.Date(datetime.date(year,month,day - 1))

    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)

    lunation = (date-pnm)/(nnm-pnm)

    return (lunation + 0.5) % 1

def plot_spl_by_month():
    fig, ax = plt.subplots(figsize=(12, 7))

    for i, month in enumerate(months):
        ax.hist(lunations[month], weights=np.array(submissions[month]) / (24 - 19), bins=np.linspace(0, 1, 1000),
                histtype="step", color=plt.get_cmap("twilight")(i / 11), label=month.capitalize(), lw=3, cumulative=True)

    ax.legend(ncol=2, loc='upper left')

    ax.set(xlabel="Lunation", ylabel="Cumulative monthly submissions")

    for i in np.arange(0, 1.1, 0.1):
        moon.draw_phase(i * 360, fig=fig, ax=ax, show=False, r=0.03, x0=i, y0=ax.get_ylim()[1] * 1.07)

    plt.savefig("figures/neocp-lunation-by-month.pdf", bbox_inches="tight", format="pdf", dpi=300)
    plt.show()


def plot_spl_overall():

    fig, ax = plt.subplots(figsize=(12, 7))

    all_lunations = []
    all_submissions = []

    for month in months:
        all_lunations.extend(lunations[month])
        all_submissions.extend(submissions[month])

    print(np.percentile(all_submissions, [1, 50, 99]))

    color = plt.get_cmap("cividis")(0.2)
    ax.hist(all_lunations, weights=np.array(all_submissions) / (24 - 19) / (365 / 29.5), bins=np.linspace(0, 1, 30), alpha=1, lw=2, color=color, edgecolor="white")

    ax.set(xlabel="Lunation", ylabel="Approximate\nsubmissions per night")

    for i in np.arange(0, 1.1, 0.1):
        moon.draw_phase(i * 360, fig=fig, ax=ax, show=False, r=0.03, x0=i, y0=ax.get_ylim()[1] * 1.07)

    plt.savefig("figures/neocp-lunation-overall.pdf", bbox_inches="tight", format="pdf", dpi=300)
    plt.show()

lunations = defaultdict(list)
submissions = defaultdict(list)

months = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july', 'aug', 'sept', 'oct', 'nov', 'dec']

sub_dict = data.get_submissions()

for year in range(2019, 2024):
    for month in sub_dict[year]:
        days, counts = np.unique(np.floor(sub_dict[year][month]).astype(int), return_counts=True)
        lunations[month].extend([get_phase_on_day(year, months.index(month) + 1, day) for day in days])
        submissions[month].extend(counts)

plot_spl_by_month()
plot_spl_overall()