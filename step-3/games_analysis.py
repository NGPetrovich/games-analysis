import pandas as pd

rtps_df = pd.read_excel("expected_rtps.xlsx")
games_df = pd.read_excel("games_analysis_merged.xlsx")

# Some game providers put 98.1-98.5 RTP. So, it's no longer a number:
# Make sure that rtp is not 0.99, though!!
rtps_df['% RTP'] = pd.to_numeric(rtps_df['% RTP'], errors='coerce').fillna(0)

games_df['Game Margin %'] = (games_df['GGR'] / games_df['Bet amount'] * 100).fillna(0)

merged_df = games_df.merge(rtps_df[['Game RTP Identifier', '% RTP']], on='Game RTP Identifier', how='left')

merged_df['Real RTP %'] = 100 - merged_df['Game Margin %']

merged_df['RTP Diff %'] = merged_df['% RTP'] - merged_df['Real RTP %']

result = '../step-4/result.xlsx'
merged_df.to_excel(result, index=False)

print(f"The merged file has been saved as {result}")
