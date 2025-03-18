import os
import uvicorn
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "sentiment-analysis"
COLLECTION_NAME = "posts"

# Lifespan function to manage database connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URI)  # Create MongoDB client
    app.state.db = client[DB_NAME]  # Store database in FastAPI state
    yield  # Run the app
    print("Closing MongoDB connection...")
    client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    try:
        db = app.state.db  # Retrieve database instance from app.state
        cursor = db[COLLECTION_NAME].find({})
        posts = await cursor.to_list(length=None)

        if not posts:
            return {"message": "No posts found"}

        return {"posts": posts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{stock_ticker}")
async def get_ticker_posts(stock_ticker: str):
    try:
        db = app.state.db  # Retrieve database instance
        cursor = db[COLLECTION_NAME].find({"ticker": {"$in": [stock_ticker.upper()]}})
        posts = await cursor.to_list(length=None)

        if not posts:
            raise HTTPException(status_code=404, detail=f"No posts found for ticker {stock_ticker.upper()}")

        return {"ticker": stock_ticker.upper(), "posts": posts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
