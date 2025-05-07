from pydantic import BaseModel

class SystemStatusResponse(BaseModel):
    """
    Response model for the system status endpoint.
    """
    status: int
    message: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": 200,
                    "message": "System is running normally"
                }
            ]
        }
    }
