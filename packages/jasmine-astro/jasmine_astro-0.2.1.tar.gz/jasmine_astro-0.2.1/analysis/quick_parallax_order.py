import pandas as pd

# Load the dataset
general_path = '/Users/stela/Documents/Scripts/orbital_task/data/gulls_orbital_motion_extracted'
file_path = f'{general_path}/OMPLDG_croin_cassan.sample.csv'
data = pd.read_csv(file_path)
# Extract relevant columns and sort by 'piEE' in descending order
filtered_data = data[[ 'lcname', 'SubRun', 'Field', 'EventID', 'piEE', 'ObsGroup_0_FiniteSourceflag']].sort_values(by='piEE', ascending=False)
filtered_data['lcname'] = filtered_data['lcname'].str.replace('OMPLDG_croin_cassan/OMPLDG_croin', 'OMPLDG_croin')

# Save the sorted data to a new CSV file
output_path = f'{general_path}/sorted_by_piE.csv'  # Replace with your desired output file path
filtered_data.to_csv(output_path, index=False)

print(f"File saved to: {output_path}")
