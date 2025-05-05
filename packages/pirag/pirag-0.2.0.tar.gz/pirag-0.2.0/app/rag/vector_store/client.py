import requests
from pymilvus import MilvusClient
from pymilvus.exceptions import MilvusException

import app.rag.config as cfn
from app.rag.utils import connection_check


class VectorStoreClient(MilvusClient):
    def __init__(self, base_url: str, user: str, password: str, database: str, collection: str, metric_type: str):
        self.base_url = base_url
        self.user = user
        self.password = password
        self.database = database
        self.collection = collection
        self.metric_type = metric_type
        self._is_connected = True
        self._is_database_exists = True

        if self.check_connection():
            try:
                super().__init__(
                    uri = base_url,
                    db_name = database,
                    collection = collection,
                    user = user,
                    password = password,
                    metric_type = metric_type,
                )
            except MilvusException as e:
                if e.code == 800:  # database not found
                    self._is_database_exists = False
                else:
                    raise

    def check_connection(self) -> bool:
        """Check if the Milvus server is accessible"""
        try:
            requests.head(url=self.base_url, timeout=5)
        except requests.exceptions.ConnectionError:
            self._is_connected = False
            return False
        self._is_connected = True
        return True

    @connection_check
    def get_databases(self) -> list:
        """Get list of available databases"""
        if not self._is_database_exists:
            return []
        return self.list_databases()

    @connection_check
    def get_collections(self) -> list:
        """Get list of available collections"""
        if not self._is_database_exists:
            return []
        return self.list_collections()

    @connection_check
    def has_database(self, database: str) -> bool:
        """Check if database exists"""
        if not self._is_database_exists:
            return False
        return database in self.get_databases()

    @connection_check
    def has_collection(self, collection: str) -> bool:
        """Check if collection exists"""
        if not self._is_database_exists:
            return False
        return collection in self.get_collections()

client = VectorStoreClient(
    base_url = cfn.MILVUS_BASE_URL,
    user = cfn.MILVUS_USER,
    password = cfn.MILVUS_PASSWORD,
    database = cfn.MILVUS_DATABASE,
    collection = cfn.MILVUS_COLLECTION,
    metric_type = cfn.MILVUS_METRIC_TYPE,
)
