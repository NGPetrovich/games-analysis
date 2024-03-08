import pandas as pd
import glob

csv_files = glob.glob('./*.csv')
print(f'Found CSV files: {csv_files}')

# the reason I put try/except is that sometimes, csv files are opening using some other encryption.
# If latin1 does not work, search for "iso-XXXXX"

df_list = []

for file in csv_files:
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding='latin1')  
    
    print(f'Loaded file {file} with {len(df)} rows.')
    df_list.append(df)
merged_df = pd.concat(df_list, ignore_index=True)

# 'Game RTP Identifier' is needed to get RTPs from Expected RTPs table in the following step
#
# Generates a unique identifier for a game by removing backslashes, splitting the string at colon (:), and merging parts.
# 
# Parameters:
# - game (str): The game string to process.
#
# Returns:
# - str: A unique identifier for the game, or None if the format doesn't match.
#

def create_game_rtp_identifier(game):

    # Removes the backslash sign from the game string (e.g. Slicin\' -> Slicin')
    game_no_backslash = game.replace("\\", "")
    # Split the string at the ":" sign (e.g. Game Provider 1: Game Name -> [Game Provider 1] [Game Name])
    parts = game_no_backslash.split(":")
    if len(parts) > 1:
        # Take the text before ":" sign e.g. [Game Provider 1]
        before_colon = parts[0].strip()
        # Take the text after ":" sign but before "(" sign, excluding the space e.g. [Game Name]
        after_colon = parts[1].split("(")[0].strip()
        # Merge text values together and remove all spaces e.g. GameProvider1GameName
        identifier = f"{before_colon}{after_colon}".replace(" ", "")
        return identifier
    return None

# Apply the function to the 'Game' column to create 'Game RTP Identifier'
merged_df['Game RTP Identifier'] = merged_df['Game'].apply(create_game_rtp_identifier)

# Create 'Unique Identifier' based on 'Game ID' and 'Game Content'
# This one is needed to have real number of games because "Game RTP Identifier" sometimes merges some games together
# (e.g. games which have same name but different "Game ID")
# Games RTP Identifier is needed for another table (expected_rtps.xlsx), which does not have "Game ID"

# First regex extracts the first instance of text within parentheses in the 'Game' column values
merged_df['Game Content'] = merged_df['Game'].str.extract(r'\((.*?)\)')

# Combined key is created based on the game_id, underscore, and the value in parentheses
merged_df['Combined Key'] = merged_df.apply(lambda x: f"{x['Game ID']}_{x['Game Content']}", axis=1)

# Here I check the frequency of each 'Combined Key' and store the result in combined_key_counts.
combined_key_counts = merged_df['Combined Key'].value_counts()

# If there are 2 games with the same game id and the same id in parentheses, I then keep them in duplicate_keys
duplicate_keys = combined_key_counts[combined_key_counts > 1].index

# Finally, here I adding "Combined Key" + suffix of the unique number if combined key has been repeated

merged_df['Unique Identifier'] = merged_df['Combined Key'].apply(
    lambda x: f"{x}_{list(duplicate_keys).index(x) + 1}" if x in duplicate_keys else x
)

aggregated_df = merged_df.groupby('Unique Identifier').agg({
    'Game': 'first',
    'Game ID': 'first',
    'Game RTP Identifier': 'first',
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

output_excel_path = "../step-3/games_analysis_merged.xlsx"
aggregated_df.to_excel(output_excel_path, index=False)

print(f'Data successfully exported to {output_excel_path}')
