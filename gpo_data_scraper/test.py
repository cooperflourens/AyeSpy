from gpo_tools.scrape import Scraper
from gpo_tools.parse import Parser
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

df = pd.read_csv('data/congressional_hearings.csv')
df = df[df['congress_number'] >= 105]
df = df[df['congress_number'] <= 118]
ids_to_parse = df['package_id'].values

scraper = Scraper(min_congress = '118', max_congress = '118', api_key = os.environ.get("API_KEY"), 
                     db = 'postgres', user = 'coopflourens', password = '8nct4bir', 
                     host = 'localhost', update_stewart_meta = False)

scraper.scrape()

parser = Parser(db = 'postgres', user = 'coopflourens', 
                   password = '8nct4bir', host = 'localhost',
                   id_values=ids_to_parse)


parser.parse_gpo_hearings()


df = pd.DataFrame(columns=['document', 'name', 'date', 'quote'])

names = pd.read_csv('data/legislators-current.csv')


for enum, doc in enumerate(parser.results):
    for row in doc:
        document = row['jacket']
        date = row['date']
        name = row['name_full'][0]
        if name == 'NA':
            name_idx = names.loc[row['name_raw'].split(' ')[-1] == names['last_name']].index
            try:
                name = names.iloc[name_idx[0]]['full_name']
            except:
                name = row['name_raw']
        quote = row['cleaned'].replace('\n', ' ').replace('  ', ' ')
        subdf = {'document': document, 'name': name, 'date': date, 'quote': quote}
        df.loc[len(df)] = subdf
df.to_csv('data/congress_118_data.csv', index = False)

