from loguru import logger

import app.rag.config as cfn
from .client import client

def doctor():
    # Check connection
    is_connected = client.check_connection()
    if not is_connected:
        logger.error(f"- ❌ FAILED: Embedding connection ({cfn.EMBEDDING_BASE_URL})")
    else:
        logger.info(f"- ✅ PASSED: Embedding connection ({cfn.EMBEDDING_BASE_URL})")
    
    # Check model availability
    try:
        if not is_connected:
            logger.warning(f"- ⏭️  SKIPPED: Embedding model (Server is not accessible)")
        else:
            # List models
            models = client.list_models()
            if cfn.EMBEDDING_MODEL not in models:
                logger.error(f"- ❌ FAILED: Embedding model not found ({cfn.EMBEDDING_MODEL})")
            else:
                logger.info(f"- ✅ PASSED: Embedding model found (Model `{cfn.EMBEDDING_MODEL}` exists)")
    except Exception as e:
        logger.error(f"- ❌ FAILED: Embedding model check ({str(e)})")
