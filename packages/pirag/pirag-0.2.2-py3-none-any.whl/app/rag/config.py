import argparse, sys, pathlib
from loguru import logger
from dynaconf import Dynaconf
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("pirag")
except PackageNotFoundError:
    __version__ = "0.0.0"


# -- Load configuration
settings = Dynaconf(
    settings_files = ["settings.yaml"],
    envvar_prefix = False,
    load_dotenv = False,
)


# -- Loging
LOG_LEVEL: str = settings.get("LOG.LEVEL", "INFO").upper()
if LOG_LEVEL not in ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]:
    raise ValueError(f"Invalid log level: {LOG_LEVEL}. Must be one of: INFO, DEBUG, WARNING, ERROR, CRITICAL")

LOG_SAVE: bool = settings.get("LOG.SAVE", False)
LOG_DIR: str = settings.get("LOG.DIR", ".pirag/logs")

LOG_TIME_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS!UTC}Z"
LOG_FILE_FORMAT = f"{LOG_TIME_FORMAT} | {{level: <8}} | {{name}}:{{function}}:{{line}} - {{message}}"
LOG_CONSOLE_FORMAT_FULL = f"<green>{LOG_TIME_FORMAT}</green> | <level>{{level: <8}}</level> | <cyan>{{name}}</cyan>:<cyan>{{function}}</cyan>:<cyan>{{line}}</cyan> - <level>{{message}}</level>\n"
LOG_CONSOLE_FORMAT_SIMPLE = f"<green>{LOG_TIME_FORMAT}</green> | <level>{{level: <8}}</level> | <level>{{message}}</level>\n"


# -- Serving API
API_HOST: str = settings.get("API.HOST", "0.0.0.0")
API_PORT: int = settings.get("API.PORT", 8000)
API_RELOAD: bool = settings.get("API.RELOAD", True)


# -- LLM Server
LLM_BASE_URL: str = settings.get("LLM.BASE_URL", "http://localhost:11434")
LLM_API_KEY: str = settings.get("LLM.API_KEY", "llm_api_key")
LLM_MODEL: str = settings.get("LLM.MODEL", "gemma3:4b")
LLM_SERVER_TYPE: str = settings.get("LLM.SERVER_TYPE", "openai")


# -- Embedding Server
EMBEDDING_BASE_URL: str = settings.get("EMBEDDING.BASE_URL", "http://localhost:11434")
EMBEDDING_API_KEY: str = settings.get("EMBEDDING.API_KEY", "embedding_api_key")
EMBEDDING_MODEL: str = settings.get("EMBEDDING.MODEL", "nomic-embed-text:latest")
EMBEDDING_SERVER_TYPE: str = settings.get("EMBEDDING.SERVER_TYPE", "openai")
EMBEDDING_DIMENSION: int = settings.get("EMBEDDING.DIMENSION", 768)


# -- Data Warehouse
MINIO_BASE_URL: str = settings.get("MINIO.BASE_URL", "http://localhost:9000")
MINIO_ACCESS_KEY: str = settings.get("MINIO.ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY: str = settings.get("MINIO.SECRET_KEY", "minioadmin")
MINIO_BUCKET: str = settings.get("MINIO.BUCKET", "pirag")
MINIO_REGION: str = settings.get("MINIO.REGION", "us-east-1")


# -- Vector Store
MILVUS_BASE_URL: str = settings.get("MILVUS.BASE_URL", "http://localhost:19530")
MILVUS_USER: str = settings.get("MILVUS.USER", "milvus")
MILVUS_PASSWORD: str = settings.get("MILVUS.PASSWORD", "milvus")
MILVUS_DATABASE: str = settings.get("MILVUS.DATABASE", "milvus_database")
MILVUS_COLLECTION: str = settings.get("MILVUS.COLLECTION", "milvus_collection")
MILVUS_METRIC_TYPE: str = settings.get("MILVUS.METRIC_TYPE", "IP")


# -- Monitoring
LANGFUSE_BASE_URL: str = settings.get("LANGFUSE.BASE_URL", "http://localhost:8000")
LANGFUSE_API_KEY: str = settings.get("LANGFUSE.API_KEY", "langfuse_api_key")
LANGFUSE_PROJECT_ID: str = settings.get("LANGFUSE.PROJECT_ID", "langfuse_project_id")


def setup_logger(log_level: str, log_save: bool, log_dir: str):
    """Configure logger with specified level and outputs"""

    logger.remove()

    # Console handler
    logger.add(
        sink = sys.stderr,
        level = log_level,
        format = lambda record: LOG_CONSOLE_FORMAT_SIMPLE if record["level"].name == "INFO" else LOG_CONSOLE_FORMAT_FULL,
        colorize = True
    )

    if log_save:
        log_dir = pathlib.Path(log_dir)
        log_dir.mkdir(exist_ok=True, parents=True)

        # File handler
        logger.add(
            sink = log_dir / "{time:YYYYMMDD-HHmmss!UTC}Z.log",
            level = log_level,
            rotation = "100 MB",
            retention = 0,
            format = LOG_FILE_FORMAT,
            serialize = False,
            enqueue = True,
            backtrace = True,
            diagnose = True,
            catch = True
        )


# Top-level parser 
top_parser = argparse.ArgumentParser(add_help=False)
top_parser.add_argument(
    "-v", "--version",
    help = "Show the `pirag` application's version and exit",
    action = "version",
    version = f"{__version__}",
)


# Common parser
common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument(
    "-h", "--help",
    help = "Show help message and exit",
    default = argparse.SUPPRESS,
    action = "help",
)


# Chat parser
chat_parser = argparse.ArgumentParser(add_help=False)
chat_parser.add_argument(
    "-n", "--no-rag",
    help = "Do not use RAG to answer the question. Just use the LLM to answer the question.",
    action = "store_true",
)


# Doctor parser
doctor_parser = argparse.ArgumentParser(add_help=False)
doctor_parser.add_argument(
    "-r", "--resolve",
    help = "Resolve the issue",
    action = "store_true",
)
