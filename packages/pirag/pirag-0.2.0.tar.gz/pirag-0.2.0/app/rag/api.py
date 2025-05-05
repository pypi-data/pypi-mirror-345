import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from loguru import logger
import app.rag.config as cfn
from app.rag.v1.router import router as core_router

# Initialize FastAPI app
api = FastAPI(
    title = "RAG API",
    description = "API for Retrieval-Augmented Generation",
    version = cfn.__version__,
)

# Add CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/")
async def _():
    return {"message": "RAG API is running"}


@api.get("/livez")
async def _():
    return {"status": "ok"}


@api.get("/readyz")
async def _():
    return {"status": "ok"}

api.include_router(router=core_router, prefix="/v1")

def serve():
    print("Serving the RAG API...")
    print(cfn.API_HOST, cfn.API_PORT, cfn.API_RELOAD)
    uvicorn.run(
        app = "app.rag.api:api",
        host = cfn.API_HOST,
        port = cfn.API_PORT,
        reload = cfn.API_RELOAD,
    )
