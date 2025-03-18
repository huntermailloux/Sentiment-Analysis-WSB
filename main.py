import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId  # Import ObjectId
from contextlib import asynccontextmanager

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "sentiment-analysis"
COLLECTION_NAME = "posts"

# ✅ Lifespan context manager for MongoDB connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URI)
    app.state.db = client[DB_NAME]  # Store the database in app state
    yield  # Application runs here
    print("❌ Closing MongoDB connection...")
    client.close()

# ✅ Initialize FastAPI with lifespan management
app = FastAPI(lifespan=lifespan)

def serialize_document(doc):
    """Convert MongoDB document to JSON-serializable format."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

@app.get("/")
async def root(request: Request):
    """Fetch all posts from MongoDB."""
    try:
        db = request.app.state.db  # ✅ Access database from app state
        cursor = db[COLLECTION_NAME].find({})
        posts = await cursor.to_list(length=None)

        return {"posts": [serialize_document(post) for post in posts] if posts else "No posts found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{stock_ticker}")
async def get_ticker_posts(stock_ticker: str, request: Request):
    """Fetch posts based on a specific stock ticker."""
    try:
        db = request.app.state.db  # ✅ Use app state to access DB
        cursor = db[COLLECTION_NAME].find({"ticker": {"$in": [stock_ticker.upper()]}})
        posts = await cursor.to_list(length=None)

        return {"ticker": stock_ticker.upper(), "posts": [serialize_document(post) for post in posts] if posts else "No posts found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Start FastAPI without `asyncio.run()` issues
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
