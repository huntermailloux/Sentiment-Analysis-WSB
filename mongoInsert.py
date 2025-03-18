import os
import re
import pandas as pd
from transformers import pipeline, AutoTokenizer
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv
import time
import ast
load_dotenv()

# Load MongoDB connection string from environment variable
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is not set. Check your .env file or environment variables.")
print(MONGO_URI);
DB_NAME = "sentiment-analysis"
COLLECTION_NAME = "posts"

# Connect to MongoDB
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Initialize sentiment analysis pipeline
MODEL_NAME = "yiyanghkust/finbert-tone"
sentimentAnalyzer = pipeline("sentiment-analysis", model=MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

CSV_FILE = "processedWSBposts.csv"

# Function to truncate text to fit within model limits
def truncate_text(text: str) -> bool:
    tokens = tokenizer.tokenize(text)
    if len(tokens) > 510:
        return False;
    #     print(f"⚠️ Truncating long post ({len(tokens)} tokens) to 512 tokens.")
    #     tokens = tokens[:512]  # Keep only the first 512 tokens
    #     text = tokenizer.convert_tokens_to_string(tokens)
    # return text
    return True;

# Function to safely convert ticker field into a list
def process_ticker(ticker_data):
    if isinstance(ticker_data, list):
        return ticker_data  # Already a list, return as is
    if isinstance(ticker_data, str):
        try:
            # Try parsing the string as a list safely
            return ast.literal_eval(ticker_data) if ticker_data.startswith("[") and ticker_data.endswith("]") else [ticker_data]
        except (SyntaxError, ValueError):
            return [ticker_data]  # If parsing fails, wrap in a list
    return []  # Default to an empty list if None or invalid

# Function to analyze sentiment and insert into MongoDB
async def process_posts():
    start_time = time.time()
    sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
    
    try: 
        df = pd.read_csv(CSV_FILE)
        tasks = []
        print("Starting loop");
    
        for _, row in df.iterrows():
            post = str(row["post"])
            if (truncate_text(post)): # Ensure it's a viable string
                # Perform sentiment analysis
                sentiment_result = sentimentAnalyzer(post)[0]
                sentiment_score = sentiment_map.get(sentiment_result["label"], 0)
                ticker = process_ticker(row["symbols"])

                document = {"ticker": ticker, "sentiment": sentiment_score, "post": post}
                tasks.append(collection.insert_one(document))

        # Insert all posts asynchronously
        await asyncio.gather(*tasks)
        print("✅ All posts processed and stored in MongoDB.")
        end_time = time.time()
        # Calculate elapsed time in minutes
        elapsed_minutes = (end_time - start_time) / 60

        # Print result
        print(f"⏱️ Elapsed time: {elapsed_minutes:.2f} minutes")

    except Exception as e:
        print(f"❌ Error processing CSV: {e}")    
    # for post_data in redditPosts:
    #     post = post_data["post"]
    #     sentiment_result = sentimentAnalyzer(post)[0]
    #     sentiment_score = sentiment_map.get(sentiment_result["label"], 0)
    #     ticker = extract_ticker(post)

    #     document = {"ticker": ticker, "sentiment": sentiment_score, "post": post}
    #     tasks.append(collection.insert_one(document))
    
    # await asyncio.gather(*tasks)
    # print("All posts processed and stored in MongoDB.")

# Run the async function
if __name__ == "__main__":
    asyncio.run(process_posts())
