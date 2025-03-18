import pandas as pd
import ast

# Load the CSV file
file_path = "sentiment-analysis.posts.csv"
df = pd.read_csv(file_path)

# Extract unique tickers
def extract_unique_tickers(df):
    unique_tickers = set()
    
    for tickers in df['ticker'].dropna():  # Drop missing values
        try:
            tickers_list = ast.literal_eval(tickers)  # Convert string representation of list to actual list
            unique_tickers.update(tickers_list)
        except (ValueError, SyntaxError):
            print(f"Skipping invalid entry: {tickers}")
    
    return sorted(unique_tickers)

unique_tickers = extract_unique_tickers(df)

# Save the unique tickers to a new CSV file
output_file = "unique_tickers.csv"
pd.DataFrame(unique_tickers, columns=["Ticker"]).to_csv(output_file, index=False)

print(f"Unique tickers saved to {output_file}")
typescript_output = f"var stocks: any[] = {unique_tickers};"
ts_output_file = "unique_tickers.ts"
with open(ts_output_file, "w") as ts_file:
    ts_file.write(typescript_output)

print(f"Unique tickers saved to {output_file}")
print(f"TypeScript array saved to {ts_output_file}")
