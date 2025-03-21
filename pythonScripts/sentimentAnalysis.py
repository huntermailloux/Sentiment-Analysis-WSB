# SentimentAnalysisPrototype.py - COMP4990
from transformers import pipeline
# import matplotlib.pyplot as plt
import pandas as pd
import re

# Creates a pipeline or sentiment-analysis and specifies the pretrained model to use.
sentimentAnalyzer = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

# Load the stock tickers csv
stockTickersCSV = pd.read_csv("company_list.csv")

# Creates our ticker directory
tickerDirectory = {str(row["Ticker"]).upper(): str(row["Name"]).lower() for _, row in stockTickersCSV.iterrows()}

# Extracts stock tickers from posts
def extractTickers(post):
    words = re.findall(r'\b[A-Z]{2,5}\b', post.upper())  # Match uppercase words ranging from 2-5 characters (common ticker format)
    tickersFound = {ticker for ticker in words if ticker in tickerDirectory and ticker}

    # Return the found tickers
    return list(tickersFound)

# Creates a function takes a post and returns the sentiment.
def analyzeSentiment(post):
    result = sentimentAnalyzer(post)[0]

    return result["label"] # Returns the sentiment

# Example Reddit Posts from R/WallStreetBets
redditPosts = [
    {"date": "2025-01-01", "post": "GME will outperform this quarter!"},
    {"date": "2025-01-01", "post": "I really think RKT will perform well this year, it's going to the moon."},
    {"date": "2025-01-02", "post": "Selling ADSK after the squeeze, finally profitable!"},
    {"date": "2025-01-03", "post": "GME is a disaster, should've stayed away."},
    {"date": "2025-01-04", "post": "Buying more TSLA after the dip, hold strong!"},
    {"date": "2025-01-05", "post": "Stock is looking great, bullish on AAPL."},
    {"date": "2025-01-06", "post": "AMC and GME are mooning again, let's go!"},
    {"date": "2025-01-07", "post": "This sucks, NVDA outlook looks grim."}
]

# Converts the reddits posts into a dataframe
df = pd.DataFrame(redditPosts)
df["date"] = pd.to_datetime(df["date"])

df["stocks_mentioned"] = df["post"].apply(extractTickers)

# Applys the sentiment analysis to all the posts above
df["sentiment"] = df["post"].apply(analyzeSentiment)

# Extract all found stock tickers into an array
stocksFound = sorted(set(df["stocks_mentioned"].dropna().sum()))

# Print results
print("Extracted Stock Mentions from Reddit Posts:")
print(df[["date", "post", "stocks_mentioned", "sentiment"]])

print("\nAll Stock Tickers Found:")
print(stocksFound)

'''
# Prints the sentiment for each post
print("Reddit Posts:")
for item in redditPosts:
    post = item["post"]
    result = sentimentAnalyzer(post)[0] 
    print(f"Post: {post}")
    print(f"Sentiment: {result['label']}\n")

'
# Graph the sentiment by assigning them to numeric values
sentimentMap = {"Positive": 1, "Neutral": 0, "Negative": -1}
df["sentimentNumeric"] = df["sentiment"].map(sentimentMap)

# Calculates the average sentiment scores for each day
dailySentimentAverage = df.groupby("date")["sentimentNumeric"].mean().reset_index()

# Plots the sentiment over the week
plt.figure(figsize=(9, 6))
plt.plot(dailySentimentAverage["date"], dailySentimentAverage["sentimentNumeric"], marker="o", linestyle="-", label="Average Sentiment")

# Plot formatting
plt.axhline(0, color="black", linestyle="--", linewidth=1)
plt.title("GME Sentiment Analysis - First Week of 2025")
plt.ylabel("Average Sentiment (Positive = 1, Neutral = 0, Negative = -1)")
plt.xlabel("Date")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

# Change the pop out windows title
plt.gcf().canvas.manager.set_window_title("GME Sentiment Analysis - COMP4990")

# Show the completed graph
plt.show()
'''