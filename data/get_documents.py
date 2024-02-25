"""
This document will interact with the govinfo api to get all CHRG (congressional hearings) documents

"""

import requests
import json
import os
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta
import re
import numpy as np
import pickle
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

offset = 0
page_size = 1000
df = pd.DataFrame(columns=['congress_number', 'document_name', 'access_link', 'package_id', 'issue_date'])
for congress_number in range(50, 119):
    # declare dataframe
    while(True):
        # print(f'Getting documents for congress number {congress_number} and offset {offset}')
        base_url = f'https://api.govinfo.gov/collections/CHRG/1700-01-03T00%3A00%3A00Z?offset={offset}&pageSize={page_size}&congress={congress_number}&api_key={os.environ.get("API_KEY")}'
        response = requests.get(base_url)
        data = response.json()
        for document in data['packages']:
            # remove last / from the link
            access_link = document['packageLink'].split('/')
            access_link = '/'.join(access_link[:-1])
            access_link = access_link + '/htm'
            subdf = {'congress_number': congress_number, 'document_name': document['title'], 'access_link': access_link, 'package_id': document['packageId'], 'issue_date': document['dateIssued']}
            df.loc[len(df)] = subdf
        if offset+page_size > data['count']:
            offset = 0
            break
        offset += page_size

# save df to csv
df.to_csv('congressional_hearings.csv', index=False)
        


