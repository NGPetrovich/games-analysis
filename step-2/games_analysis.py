import pandas as pd

rtps_df = pd.read_excel("Expected RTPs.xlsx")
games_df = pd.read_excel("games_analysis_merged.xlsx")

# Calculate "Game Margin %"
games_df['Game Margin %'] = (games_df['GGR'] / games_df['Bet amount']).fillna(0) * 100

# Calculate the Actual RTP %
games_df['Real RTP %'] = 100 - games_df['Game Margin %']

# Merge the RTP data into the games analysis dataframe using a left join
merged_df = games_df.merge(rtps_df[['Odoo Unique Identifier', 'RTP']], on='Odoo Unique Identifier', how='left')


merged_df['RTP %'] = merged_df['RTP'] * 100

merged_df['RTP Diff %'] = merged_df['RTP %'] - merged_df['Real RTP %']

output_path = '../step-3/result.xlsx'

merged_df.to_excel(output_path, index=False)

print(f"The merged file has been saved as {output_path}")