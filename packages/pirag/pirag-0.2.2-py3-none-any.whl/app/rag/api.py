import uvicorn
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from loguru import logger
import app.rag.config as cfn

from app.rag.routers import system_router
from app.rag.v1.routers import router as v1_router

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

api.include_router(router=system_router, prefix="", tags=["System"])
api.include_router(router=v1_router, prefix="/v1")

def serve(parser_options=None):
    print("Serving the RAG API...")
    if parser_options:
        logger.debug(f"Serve parser options: {parser_options}")
        
    uvicorn.run(
        app = "app.rag.api:api",
        host = cfn.API_HOST,
        port = cfn.API_PORT,
        reload = cfn.API_RELOAD,
    )
