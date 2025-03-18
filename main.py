import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "sentiment-analysis"
COLLECTION_NAME = "posts"

app = FastAPI()

# Explicitly create a global MongoDB client
client = AsyncIOMotorClient(MONGO_URI) if MONGO_URI else None
db = client[DB_NAME] if client else None

@app.middleware("http")
async def db_middleware(request: Request, call_next):
    """Ensure that every request has access to the MongoDB database."""
    if not db:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
    
    request.state.db = db  # Attach DB to the request state
    response = await call_next(request)
    return response

@app.get("/")
async def root(request: Request):
    try:
        return {"uri": MONGO_URI}
        db = request.state.db
        cursor = db[COLLECTION_NAME].find({})
        posts = await cursor.to_list(length=None)
        return {"posts": posts if posts else "No posts found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/{stock_ticker}")
async def get_ticker_posts(stock_ticker: str, request: Request):
    try:
        db = request.state.db
        cursor = db[COLLECTION_NAME].find({"ticker": {"$in": [stock_ticker.upper()]}})
        posts = await cursor.to_list(length=None)

        if not posts:
            raise HTTPException(status_code=404, detail=f"No posts found for ticker {stock_ticker.upper()}")

        return {"ticker": stock_ticker.upper(), "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
