from loguru import logger

import app.rag.config as cfn
from .client import client

def doctor(resolve: bool):
    # Check connection
    is_connected = client.check_connection()
    if not is_connected:
        logger.error(f"- ❌ FAILED: Vector store connection ({cfn.MILVUS_BASE_URL})")
    else:
        logger.info(f"- ✅ PASSED: Vector store connection ({cfn.MILVUS_BASE_URL})")
    
    # Check databases
    databases = None
    try:
        databases = client.get_databases()
        if not is_connected:
            logger.warning("- ⏭️  SKIPPED: Vector store databases (Server is not accessible)")
        else:
            if not client.has_database(cfn.MILVUS_DATABASE):
                logger.error(f"- ❌ FAILED: Vector store databases (Database '{cfn.MILVUS_DATABASE}' not found)")
                if resolve:
                    logger.info(f"- 🔧 Resolving issue: Creating database '{cfn.MILVUS_DATABASE}'")
                    client.create_database(cfn.MILVUS_DATABASE)
            else:
                logger.info(f"- ✅ PASSED: Vector store databases (Database '{cfn.MILVUS_DATABASE}' exists)")
    except Exception as e:
        logger.error(f"- ❌ FAILED: Database check ({str(e)})")
    
    # Check collections
    try:
        collections = client.get_collections()
        if not is_connected:
            logger.warning("- ⏭️  SKIPPED: Vector store collections (Server is not accessible)")
        elif len(databases) == 0:
            logger.warning("- ⏭️  SKIPPED: Vector store collections (No database available)")
        elif len(collections) == 0:
            logger.error("- ❌ FAILED: Vector store collections (No collections available)")
            if resolve:
                logger.info(f"- 🔧 Resolving issue: Creating collection '{cfn.MILVUS_COLLECTION}'")
                client.create_collection(cfn.MILVUS_COLLECTION)
        else:
            if not client.has_collection(cfn.MILVUS_COLLECTION):
                logger.error(f"- ❌ FAILED: Vector store collections (Collection '{cfn.MILVUS_COLLECTION}' not found)")
                if resolve:
                    logger.info(f"- 🔧 Resolving issue: Creating collection '{cfn.MILVUS_COLLECTION}'")
                    client.create_collection(
                        collection_name = cfn.MILVUS_COLLECTION,
                        dimension = cfn.EMBEDDING_DIMENSION,
                        metric_type = cfn.MILVUS_METRIC_TYPE
                    )
            else:
                logger.info(f"- ✅ PASSED: Vector store collections (Collection '{cfn.MILVUS_COLLECTION}' exists)")
    except Exception as e:
        logger.error(f"- ❌ FAILED: Collection check ({str(e)})")
