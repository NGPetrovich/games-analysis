import pandas as pd
import glob

excel_files = glob.glob('./*.xlsx')
print(f'Found Excel files: {excel_files}')

# in case I forget to delete the old excel file or to add the minmaxbetamountmaxwinning.xslx from the server:
input_excel_path = excel_files[0] if excel_files else None

output_excel_path = '../step-3/expected_rtps.xlsx'

# ALWAYS make sure that the name of columns in the file are as below:
required_columns = ['Game Provider', 'Game Name', '% RTP']

merged_data = pd.DataFrame()

if input_excel_path:
    xls = pd.ExcelFile(input_excel_path)

    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            if all(col in df.columns for col in required_columns):
                # Retain only the required columns and make a copy to avoid SettingWithCopyWarning error!!
                df_filtered = df[required_columns].copy()

                # Generate a 'Game RTP Identifier' by concatenating the 'Game Provider' and 'Game Name' without spaces.
                df_filtered['Game RTP Identifier'] = df_filtered['Game Provider'].str.replace(' ', '') + df_filtered['Game Name'].str.replace(' ', '')

                merged_data = pd.concat([merged_data, df_filtered], ignore_index=True)
        except Exception as e:
            print(f"Error processing sheet {sheet_name}: {e}")

    merged_data.to_excel(output_excel_path, index=False)
else:
    print("No Excel files found in the current directory.")

print(f'Data successfully exported to {output_excel_path}')
