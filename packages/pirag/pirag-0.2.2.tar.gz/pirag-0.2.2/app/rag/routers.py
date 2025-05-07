from fastapi import APIRouter

from .models import SystemStatusResponse

system_router = APIRouter()

@system_router.get(
    path = "/",
    summary = "Root Endpoint",
    description = "Root endpoint for the RAG API",
    response_model = SystemStatusResponse,
)
async def root():
    return SystemStatusResponse(
        status = 200,
        message = "RAG API is running. If you want to see API documentation, please visit /docs",
    )

@system_router.get(
    path = "/livez",
    summary = "Liveness Probe",
    description = "Check if the RAG API is running",
    response_model = SystemStatusResponse,
)
async def livez():
    return SystemStatusResponse(
        status = 200,
        message = "RAG API is live",
    )

@system_router.get(
    path = "/readyz",
    summary = "Readiness Probe",
    description = "Check if the RAG API is ready to serve requests",
    response_model = SystemStatusResponse,
)
async def readyz():
    return SystemStatusResponse(
        status = 200,
        message = "RAG API is ready to serve requests",
    )
