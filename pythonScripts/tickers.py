import pandas as pd
import json

# Load the JSON file
file_path = "sentiment-analysis.posts.json"
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)

# Extract unique tickers
def extract_unique_tickers(df):
    unique_tickers = set()
    
    for tickers in df['ticker'].dropna():  # Drop missing values
        if isinstance(tickers, list):  # Ensure it's a list
            unique_tickers.update(tickers)
        else:
            print(f"Skipping invalid entry: {tickers}")
    
    return sorted(unique_tickers)

unique_tickers = extract_unique_tickers(df)

# Save the unique tickers to a new CSV file
output_file = "unique_tickers.csv"
pd.DataFrame(unique_tickers, columns=["Ticker"]).to_csv(output_file, index=False)

print(f"Unique tickers saved to {output_file}")

# Save as TypeScript array
typescript_output = f"var stocks: any[] = {unique_tickers};"
ts_output_file = "unique_tickers.ts"
with open(ts_output_file, "w", encoding="utf-8") as ts_file:
    ts_file.write(typescript_output)

print(f"TypeScript array saved to {ts_output_file}")
