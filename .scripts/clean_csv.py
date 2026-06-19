import pandas as pd

print("Loading CSV...")
df = pd.read_csv('bengaluru_house_prices.csv')

# 1. Fill blank in society as "Private Property"
if 'society' in df.columns:
    df['society'] = df['society'].fillna('Private Property')

# 2. Fill blank in balcony as zero
if 'balcony' in df.columns:
    df['balcony'] = df['balcony'].fillna(0)

# 3. Replace blank in bath to same number as size (BHK)
if 'bath' in df.columns and 'size' in df.columns:
    def extract_bhk(x):
        try:
            return int(str(x).split(' ')[0])
        except:
            return None
            
    bhk_values = df['size'].apply(extract_bhk)
    df['bath'] = df['bath'].fillna(bhk_values)

print("Saving updated CSV to bengaluru_house_prices_cleaned.csv...")
df.to_csv('bengaluru_house_prices_cleaned.csv', index=False)
print("CSV successfully cleaned and saved as new file!")
