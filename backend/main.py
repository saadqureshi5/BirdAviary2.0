from __future__ import annotations
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import birds, categories, pairings, breeding, sales, dna, reminders, soft_food, expenses, activity, sync, auth
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load .env from the project root (parent of backend/)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    os.makedirs("uploads/dna", exist_ok=True)
    yield

app = FastAPI(title="Bird Aviary API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(birds.router, prefix="/api/birds", tags=["birds"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(pairings.router, prefix="/api/pairings", tags=["pairings"])
app.include_router(breeding.router, prefix="/api/breeding", tags=["breeding"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(dna.router, prefix="/api/dna", tags=["dna"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(soft_food.router, prefix="/api/soft-food", tags=["soft-food"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(activity.router, prefix="/api/activity", tags=["activity"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8008, help="Port to run the server on")
    args = parser.parse_args()
    uvicorn.run("main:app", host="0.0.0.0", port=args.port, reload=True)
