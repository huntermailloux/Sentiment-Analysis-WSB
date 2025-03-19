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

def filter_valid_posts(df):
    """Filters out posts that exceed token limits."""
    print("🔍 Filtering out long posts...")
    df["valid"] = df["post"].apply(lambda x: len(tokenizer.tokenize(str(x))) <= 510)
    filtered_df = df[df["valid"]].drop(columns=["valid"])
    print(f"✅ {len(filtered_df)} valid posts remaining after filtering.")
    return filtered_df

def process_ticker(ticker_data):
    if isinstance(ticker_data, list):
        return ticker_data
    if isinstance(ticker_data, str):
        try:
            return ast.literal_eval(ticker_data) if ticker_data.startswith("[") and ticker_data.endswith("]") else [ticker_data]
        except (SyntaxError, ValueError):
            return [ticker_data]
    return []

async def analyze_sentiment(post):
    return sentimentAnalyzer(post)[0]

async def process_posts():
    start_time = time.time()
    sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
    
    try:
        print("📂 Loading CSV file...")
        df = pd.read_csv(CSV_FILE)
        print(f"✅ Loaded {len(df)} posts from CSV.")

        df = filter_valid_posts(df)
        print("🔄 Processing ticker symbols...")
        df["ticker"] = df["symbols"].apply(process_ticker)

        print("🛠️ Processing and inserting documents...")
        for _, row in tqdm(df.iterrows(), total=len(df), desc="🔄 Inserting Posts"):
            sentiment_result = await analyze_sentiment(str(row["post"]))
            document = {
                "ticker": row["ticker"],
                "sentiment": sentiment_map.get(sentiment_result["label"], 0),
                "date": row["date"],
                "preprocessedPost": row["post"],
                "originalPost": row["body"]
            }
            await collection.insert_one(document)
        
        elapsed_time = (time.time() - start_time) / 60
        print(f"✅ All posts stored successfully in MongoDB!")
        print(f"⏱️ Total elapsed time: {elapsed_time:.2f} minutes")

    except Exception as e:
        print(f"❌ Error processing CSV: {e}")

if __name__ == "__main__":
    print("🚀 Starting script...")
    asyncio.run(process_posts())
    print("🏁 Done! 🎉")
