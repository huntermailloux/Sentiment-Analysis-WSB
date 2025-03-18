import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId  # Import ObjectId from bson

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "sentiment-analysis"
COLLECTION_NAME = "posts"

app = FastAPI()

# Create MongoDB client
client = AsyncIOMotorClient(MONGO_URI) if MONGO_URI else None
db = client[DB_NAME] if client else None

@app.middleware("http")
async def db_middleware(request: Request, call_next):
    """Ensure that every request has access to the MongoDB database."""
    if db is None:  # ✅ Explicitly check if db is None
        raise HTTPException(status_code=500, detail="Database connection not initialized")

    request.state.db = db  # Attach DB to the request state
    response = await call_next(request)
    return response

def serialize_document(doc):
    """Convert MongoDB document to JSON-serializable format."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

@app.get("/")
async def root(request: Request):
    try:
        db = request.state.db
        cursor = db[COLLECTION_NAME].find({})
        posts = await cursor.to_list(length=None)

        # Convert ObjectId to string in all documents
        posts = [serialize_document(post) for post in posts]

        return {"posts": posts if posts else "No posts found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{stock_ticker}")
async def get_ticker_posts(stock_ticker: str, request: Request):
    try:
        db = request.state.db
        cursor = db[COLLECTION_NAME].find({"ticker": {"$in": [stock_ticker.upper()]}})
        posts = await cursor.to_list(length=None)  # ✅ Await the cursor

        # Convert ObjectId to string in all documents
        posts = [serialize_document(post) for post in posts]

        return {"ticker": stock_ticker.upper(), "posts": posts if posts else "No posts found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
