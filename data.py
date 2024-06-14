import requests
import re
from collections import defaultdict
import os
import bs4
import numpy as np

def get_submissions(year_range=range(2002, 2024), file_path="data/neocp-rates.npy"):

    # regex to find the date in the submission text
    date_regex = r"\((\w+)\.* (\d+\.\d+) UT\)"

    # check if we have already saved the data
    if os.path.exists(file_path):
        all_submissions = np.load(file_path, allow_pickle=True).item()
    else:
        all_submissions = {}

        # go through each year
        for year in year_range:
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
    return all_submissions