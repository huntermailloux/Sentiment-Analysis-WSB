import pandas as pd

# Load the CSV files
symbols_file = "symbols.csv"
unique_tickers_file = "unique_tickers.csv"
output_csv = "filtered_stocks.csv"
ts_output = "stocks.ts"

# Read unique tickers
unique_tickers_df = pd.read_csv(unique_tickers_file)
unique_tickers = set(unique_tickers_df.iloc[:, 0])  # Assuming tickers are in the first column

# Read symbols with names
symbols_df = pd.read_csv(symbols_file)

# Filter the symbols to keep only those in unique_tickers
filtered_df = symbols_df[symbols_df.iloc[:, 0].isin(unique_tickers)]

# Save the filtered data to a new CSV
filtered_df.to_csv(output_csv, index=False)

# Convert to TypeScript format
ts_data = (
    "var stocks: any[] = [" + 
    ", ".join([f"{{ticker: \"{row[0]}\", name: \"{row[1]}\"}}" for row in filtered_df.values]) + 
    "]"
)

# Save to TypeScript file
with open(ts_output, "w") as ts_file:
    ts_file.write(ts_data)

print(f"Filtered data saved to {output_csv}")
print(f"TypeScript variable saved to {ts_output}")