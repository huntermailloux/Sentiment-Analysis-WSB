import os
import uvicorn
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "sentiment-analysis"
COLLECTION_NAME = "posts"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/ticker/{stock_ticker}")
async def get_ticker_posts(stock_ticker: str):
    try:
        # Fetch posts where "ticker" matches the stock_ticker from the URL
        cursor = collection.find({"ticker": stock_ticker.upper()})  # Ensure case insensitivity
        posts = await cursor.to_list(length=None)  # Convert cursor to list
        
        if not posts:
            raise HTTPException(status_code=404, detail=f"No posts found for ticker {stock_ticker.upper()}")

        return {"ticker": stock_ticker.upper(), "posts": posts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)