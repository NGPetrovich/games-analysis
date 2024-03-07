# python games_merger.py

import pandas as pd
import glob

csv_files = glob.glob('./*.csv')
print(f'Found CSV files: {csv_files}')

# Because csv files sometimes encoded differently, I needed to add try/catch ('iso-8859-1' or 'unicode_escape') 
df_list = []
for file in csv_files:
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding='latin1')  
    
    print(f'Loaded file {file} with {len(df)} rows.')

    df_list.append(df)
merged_df = pd.concat(df_list, ignore_index=True)

# Created 'Odoo Unique Identifier' based on 'Game ID' and contents within parentheses in 'Game'
# I called it "Odoo" because I added information about it to ticket in Odoo

merged_df['Game Content'] = merged_df['Game'].str.extract(r'\((.*?)\)')

# Because of stupid MrSlotty games, had to create a combined key of 'Game ID' and 'Game Content'

merged_df['Combined Key'] = merged_df.apply(lambda x: f"{x['Game ID']}_{x['Game Content']}", axis=1)

# Identify non-unique 'Game Content' within the same 'Game ID'
combined_key_counts = merged_df['Combined Key'].value_counts()
duplicate_keys = combined_key_counts[combined_key_counts > 1].index

# Mark duplicates with an index suffix to ensure uniqueness
merged_df['Odoo Unique Identifier'] = merged_df['Combined Key'].apply(
    lambda x: f"{x}_{list(duplicate_keys).index(x) + 1}" if x in duplicate_keys else x
)

# Learn about "Odoo Unique Identifier" from Odoo's Project, where I documented it
aggregated_df = merged_df.groupby('Odoo Unique Identifier').agg({
    'Game': 'first',
    'Game ID': 'first',
    'Unique users': 'sum',
    'Bet count': 'sum',
    'Bet amount': 'sum',
    'Win count': 'sum',
    'Win amount': 'sum',
    'Count of SideBet bets': 'sum',
    'Amount of SideBet bets': 'sum',
    'Count of SideBet wins': 'sum',
    'Amount of SideBet wins': 'sum',
    'Count of Jackpot bets': 'sum',
    'Amount of Jackpot bets': 'sum',
    'Count of Jackpot wins': 'sum',
    'Amount of Jackpot wins': 'sum',
    'Free Round wins': 'sum',
    'GGR': 'sum',
    'Launch count': 'sum',
    'Other bets': 'sum',
    'Other wins': 'sum'
}).reset_index()

export_name = "../step-2/games_analysis_merged.xlsx"
aggregated_df.to_excel(export_name, index=False)

print(f'Data successfully exported to {export_name}')
