from loguru import logger

import app.rag.config as cfn
from .client import client

def doctor(resolve: bool):
    # Check connection
    is_connected = client.check_connection()
    if not is_connected:
        logger.error(f"- ❌ FAILED: LLM connection ({cfn.LLM_BASE_URL})")
    else:
        logger.info(f"- ✅ PASSED: LLM connection ({cfn.LLM_BASE_URL})")
    
    # Check model availability
    try:
        if not is_connected:
            logger.warning(f"- ⏭️  SKIPPED: LLM model (Server is not accessible)")
        else:
            # List models
            models = client.list_models()
            if cfn.LLM_MODEL not in models:
                logger.error(f"- ❌ FAILED: LLM model not found ({cfn.LLM_MODEL})")
            else:
                logger.info(f"- ✅ PASSED: LLM model found (Model `{cfn.LLM_MODEL}` exists)")
    except Exception as e:
        logger.error(f"- ❌ FAILED: LLM model check ({str(e)})")
