# SentimentAnalysisPrototype.py - COMP4990
from transformers import pipeline
import matplotlib.pyplot as plt
import pandas as pd

# Creates a pipeline or sentiment-analysis and specifies the pretrained model to use.
sentimentAnalyzer = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

# Example Reddit Posts from R/WallStreetBets
redditPosts = [
    {"date": "2025-01-01", "post": "GME will outperform this quarter!"},
    {"date": "2025-01-01", "post": "I really think gamestop will perform well this year, it's going to the moon."},
    {"date": "2025-01-01", "post": "Not sure on GME anymore."},
    {"date": "2025-01-01", "post": "I'm going all in on gamestop look at the positive trend!."},
    {"date": "2025-01-02", "post": "Selling GME after the squeeze, finally profitable!"},
    {"date": "2025-01-02", "post": "GME is not looking great anymore."},
    {"date": "2025-01-03", "post": "GME is a disaster, should've stayed away."},
    {"date": "2025-01-03", "post": "Regret investing in GME, big losses."},
    {"date": "2025-01-04", "post": "Buying more GME on the dip, hold strong!"},
    {"date": "2025-01-04", "post": "GME has potential, keep holding!"},
    {"date": "2025-01-05", "post": "Regret holding GME, total loss."},
    {"date": "2025-01-05", "post": "Still holding GME, hoping for a turnaround."},
    {"date": "2025-01-06", "post": "GME is mooning again, let's go!"},
    {"date": "2025-01-06", "post": "GME to the moon, diamond hands!"},
    {"date": "2025-01-07", "post": "WOW it crashed I can't believe it, GME sucks"},
    {"date": "2025-01-07", "post": "This sucks GME outlook looks grim."},
    {"date": "2025-01-07", "post": "Gamestop made me lose everything."},
    {"date": "2025-01-07", "post": "I still believe that GME will do good!"}
]

# Converts the reddits posts into a dataframe
df = pd.DataFrame(redditPosts)

# Creates a function takes a post and returns the sentiment.
def analyzeSentiment(post):
    result = sentimentAnalyzer(post)[0]
    return result["label"] # Returns the sentiment

# Applys the sentiment analysis to all the posts above
df["sentiment"] = df["post"].apply(analyzeSentiment)
df["date"] = pd.to_datetime(df["date"])

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

# Prints the sentiment for each post
print("Reddit Posts:")
for item in redditPosts:
    post = item["post"]
    result = sentimentAnalyzer(post)[0] 
    print(f"Post: {post}")
    print(f"Sentiment: {result['label']}\n")


# Show the completed graph
plt.show()