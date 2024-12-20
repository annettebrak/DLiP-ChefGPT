import pandas as pd
import re

flavour_DB_path = 'chefgpt/resources/flavourDB2_molecules.csv'
nevo_path = 'chefgpt/resources/NEVO_Joined_cleaned.csv'

flavour_df = pd.read_csv(flavour_DB_path)
nevo_df = pd.read_csv(nevo_path, sep=';')

flavour_df['clean_ingredient'] = flavour_df['ingredient'].apply(
    lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x).lower().strip()))
nevo_df['clean_flavour_name'] = nevo_df['flavour_name'].apply(
    lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x).lower().strip()))

nevo_df.rename(columns={'flavour_index': 'ID'}, inplace=True)
nevo_df['ID'] = nevo_df['ID'].dropna().astype(int).astype(str)

non_numeric_columns = nevo_df.select_dtypes(exclude='number').columns
numeric_columns = nevo_df.select_dtypes(include='number').columns

nevo_df_grouped = (
    nevo_df.groupby(['clean_flavour_name', 'ID'], as_index=False)
    .agg({**{col: 'first' for col in non_numeric_columns}, **{col: 'mean' for col in numeric_columns}})
)

combined_df = pd.merge(
    flavour_df,
    nevo_df_grouped,
    how='inner',  
    left_on='clean_ingredient',
    right_on='clean_flavour_name'
)

print(combined_df.columns)

molecules_column = combined_df.pop('molecule_list')
combined_df['molecule_list'] = molecules_column
nevo_df_names = nevo_df[['Engelse naam/Food name', 'flavour_name']]
nevo_df_names.to_csv('chefgpt/resources/nevo_names.csv', index=False)
output_path = 'chefgpt/resources/combined_flavour_nutrition.csv'
combined_df.to_csv(output_path, index=False)
print(f"saved to {output_path}")
