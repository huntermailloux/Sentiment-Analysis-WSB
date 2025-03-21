import os
import pandas as pd
import ast
import time
import asyncio
from tqdm import tqdm
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is not set. Check your .env file or environment variables.")
print(f"✅ Connected to MongoDB at {MONGO_URI}")

DB_NAME = "sentiment-analysis"
COLLECTION_NAME = "postsV2"
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Initialize sentiment analysis pipeline
MODEL_NAME = "yiyanghkust/finbert-tone"
print("⏳ Loading sentiment analysis model...")
sentimentAnalyzer = pipeline("sentiment-analysis", model=MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
print("✅ Model loaded successfully!")

CSV_FILE = "processedWSBposts.csv"

# Function to truncate text in batch
def filter_valid_posts(df):
    """Filters out posts that exceed token limits for batch processing"""
    print("🔍 Filtering out long posts...")
    df["valid"] = df["post"].apply(lambda x: len(tokenizer.tokenize(str(x))) <= 510)
    filtered_df = df[df["valid"]].drop(columns=["valid"])
    print(f"✅ {len(filtered_df)} valid posts remaining after filtering.")
    return filtered_df

# Function to safely convert ticker field into a list
def process_ticker(ticker_data):
    if isinstance(ticker_data, list):
        return ticker_data
    if isinstance(ticker_data, str):
        try:
            return ast.literal_eval(ticker_data) if ticker_data.startswith("[") and ticker_data.endswith("]") else [ticker_data]
        except (SyntaxError, ValueError):
            return [ticker_data]
    return []

# Function to analyze sentiment in batches
async def analyze_sentiment_batch(posts):
    print("⚡ Running sentiment analysis...")
    results = sentimentAnalyzer(posts)
    print("✅ Sentiment analysis completed!")
    return results

# Function to process and insert posts into MongoDB
async def process_posts():
    start_time = time.time()
    sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}

    try:
        print("📂 Loading CSV file...")
        df = pd.read_csv(CSV_FILE)
        print(f"✅ Loaded {len(df)} posts from CSV.")

        # Filter out long posts
        df = filter_valid_posts(df)

        # Process tickers
        print("🔄 Processing ticker symbols...")
        df["ticker"] = df["symbols"].apply(process_ticker)

        posts = df["post"].astype(str).tolist()
        sentiment_results = await analyze_sentiment_batch(posts)

        # Prepare documents for bulk insertion
        print("🛠️ Preparing documents for MongoDB...")
        documents = [
            {
                "ticker": ticker,
                "sentiment": sentiment_map.get(result["label"], 0),
                "date": date,
                "preprocessedPost": post,
                "originalPost": body
            }
            for ticker, date, post, body, result in tqdm(
                zip(df["ticker"], df["date"], df["post"], df["body"], sentiment_results),
                total=len(posts),
                desc="🔄 Processing Posts"
            )
        ]
        print("✅ Documents prepared.")

        # Batch insert into MongoDB
        if documents:
            print("📤 Inserting into MongoDB (batch)...")
            await collection.insert_many(documents)
            print(f"✅ {len(documents)} posts stored successfully in MongoDB!")

        elapsed_time = (time.time() - start_time) / 60
        print(f"⏱️ Total elapsed time: {elapsed_time:.2f} minutes")

    except Exception as e:
        print(f"❌ Error processing CSV: {e}")

if __name__ == "__main__":
    print("🚀 Starting script...")
    asyncio.run(process_posts())
    print("🏁 Done! 🎉")
