import requests
import re
from collections import defaultdict
import os

import bs4
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

def plot_monthly(all_years=True, show=True, save=None):
    fig, ax = plt.subplots()

    bounds = np.arange(2002, 2025) - 0.5
    norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=256)

    for year in avg_per_day if all_years else [2023]:
        if year == 2023:
            ax.errorbar(months_full, [avg_per_day[year][month] for month in months],
                        yerr=[std_per_day[year][month] for month in months],
                        label=year, fmt='o' if all_years else "o-", capsize=5, capthick=3, markersize=15, lw=3,
                        color=plt.get_cmap('cividis_r')(1.0))
        else:
            scatter = ax.scatter(months_full, [avg_per_day[year][month] for month in months], label=year, cmap='cividis_r',
                                c=np.repeat(year, len(months)), norm=norm, s=50 if year != 2023 else 100, ec='none')
            # ax.errorbar(months_full, [avg_per_day[year][month] for month in months], yerr=[std_per_day[year][month] for month in months],
            #             label=year, c='k', fmt='o', capsize=5, capthick=2, markersize=5, zorder=-1)

    if all_years:
        fig.colorbar(scatter, label='Year', ticks=np.arange(2002, 2024))

    ax.set(xlabel='Month', ylabel='Median submissions per day')

    if save is not None:
        plt.savefig(save, format='pdf', bbox_inches='tight', dpi=300)

    if show:
        plt.show()
    

def plot_yearly(show=True, save=False):
    fig, ax = plt.subplots()

    yearly_totals = [np.sum(list(total_per_day[year].values())) for year in total_per_day]

    for year_range, name, l in zip([[2002, 2023.5], [2010, 2014], [2015, 2023.5]],
                                   ['Catalina Sky Survey already operational', 'Pan-STARRS starts', 'ATLAS starts'],
                                   [3400, 3500, 2000]):
        ax.axvline(year_range[0], 0, l / 6800, lw=2, color="grey")
        ax.annotate(name, (year_range[0], l), fontsize=0.6*fs, va='center', ha='center', color='k', rotation=90,
                    bbox=dict(facecolor='w', edgecolor='w', boxstyle='round,pad=0.2'))

    ax.plot(np.arange(2002, 2024), yearly_totals, marker='o', lw=3, markersize=15, color=plt.get_cmap('cividis_r')(1.0))

    ax.set(xlabel='Year', ylabel='Total submissions per year', xlim=(2001.5, 2023.5), xticks=np.arange(2002, 2024), xticklabels=np.arange(2002, 2024))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    ax.grid(axis='y')

    if save is not None:
        plt.savefig(save, format='pdf', bbox_inches='tight', dpi=300)

    if show:
        plt.show()

# regex to find the date in the submission text
date_regex = r"\((\w+)\.* (\d+\.\d+) UT\)"

# check if we have already saved the data
file_path = "data/neocp-rates.npy"
if os.path.exists(file_path):
    all_submissions = np.load(file_path, allow_pickle=True).item()
else:
    all_submissions = {}

    # go through each year
    for year in range(2002, 2024):
        print(f"Getting data for {year}...")

        # grab the html and parse it
        r = requests.get(f'https://birtwhistle.org.uk/NEOCPObjects{year}.htm')
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        # get the text specifically about submissions
        submission_text_objs = soup.find_all(name='font', attrs={'face': 'Courier New'})
        submissions = defaultdict(list)

        for submission_text_obj in submission_text_objs:
            submission_text = submission_text_obj.text
            print(len(submission_text.split("\n")))

            # find each date in the submissions with the regex
            matches = re.finditer(date_regex, submission_text, re.MULTILINE)

            # add each date separately to the list
            for match in matches:
                month = match.group(1)
                day = match.group(2)
                submissions[month.lower()].append(float(day))
                
            all_submissions[year] = submissions

    np.save(file_path, all_submissions)

print("All submissions processed.")

months = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july', 'aug', 'sept', 'oct', 'nov', 'dec']
months_full = [m.capitalize() for m in months]

# turn it into a dictionary of years, months and then submissions per day
avg_per_day = all_submissions.copy()
total_per_day  = {}
std_per_day = {}
for year in avg_per_day:
    std_per_day[year] = {}
    total_per_day[year] = {}
    for month in months:
        if month not in avg_per_day[year]:
            avg_per_day[year][month] = np.nan
            total_per_day[year][month] = 0
            std_per_day[year][month] = np.nan
        else:
            days = np.floor(avg_per_day[year][month]).astype(int)
            u, counts = np.unique(days, return_counts=True)
            avg_per_day[year][month] = np.mean(counts)

            total_per_day[year][month] = np.sum(counts)

            # bootstrap the mean
            # draw a random sample with replacement of the shape ((len(counts), n_samples) and take the mean of each column
            samples = np.random.choice(counts, (len(counts), 1000), replace=True)
            std_per_day[year][month] = np.std(np.mean(samples, axis=0))

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

plot_monthly(show=False, save="figures/neocp-historical-monthly-all.pdf")
plot_monthly(show=False, all_years=False, save="figures/neocp-historical-monthly-2023.pdf")

plt.close('all')
plot_yearly(show=True, save="figures/neocp-historical-years.pdf")

# print out the month average for the past 3 years
for year in range(2021, 2024):
    all_month_avg = np.percentile([avg_per_day[year][month] for month in months], [5, 50, 95])
    print(f"{year}: {all_month_avg}")

