# -*- coding: utf-8 -*-
from datetime import datetime, timezone

from pip_services4_config.connect import ConnectionParams

from ..data.version1.ModelRequestV1 import ModelRequestV1
from ..data.version1.ModelResponseV1 import ModelResponseV1
from .IModelConnector import IModelConnector

class DeepSeekModelConnector(IModelConnector):
    
    def __init__(self, connection_params: ConnectionParams):
        # Copy connection params obj
        self.connection_params = ConnectionParams.from_string(connection_params.to_string())
        ## TODO: set protocol, host, port, uri
        # Add timestamp
        self.time_created = str(datetime.now(timezone.utc))
        # Hash connection params
        self.hash_id = self._hash_connection_params(self.connection_params)

    def _hash_connection_params(self, connection_params: ConnectionParams) -> str:
        return str(hash(connection_params.to_string()))

    def execute_request(self, model_request: ModelRequestV1) -> ModelResponseV1:
        return ModelResponseV1(value="DeepSeek not implemented yet")
