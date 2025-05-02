# -*- coding: utf-8 -*-
from datetime import datetime, timezone

from pip_services4_config.connect import ConnectionParams

from ..data.version1.ModelRequestV1 import ModelRequestV1
from ..data.version1.ModelResponseV1 import ModelResponseV1
from .IModelConnector import IModelConnector

import openai

class OpenAIModelConnector(IModelConnector):
    
    def __init__(self, connection_params: ConnectionParams):
        # Copy connection params obj
        self.connection_params = ConnectionParams.from_string(connection_params.to_string())
        # Add timestamp
        self.time_created = str(datetime.now(timezone.utc))
        # Hash connection params
        self.hash_id = self._hash_connection_params(self.connection_params)

        # TODO:
        self.api_key = self.connection_params.get_as_nullable_string("api_key")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            raise ValueError("API key is required to connect to OpenAI")
        
        openai.base_url = self.connection_params.get_as_nullable_string("base_url") or "https://api.openai.com/v1"

    def _hash_connection_params(self, connection_params: ConnectionParams) -> str:
        return str(hash(connection_params.to_string()))

    def execute_request(self, model_request: ModelRequestV1) -> ModelResponseV1:
        if model_request.model_name is None or model_request.model_name == "":
            model_request.model_name = "gpt-3.5-turbo-instruct"

        try:
            response = openai.completions.create(
                model=model_request.model_name,
                prompt=[model_request.value]
            )
            result = response.choices[0].text
            return ModelResponseV1(value=result)
        except Exception as e:
            return ModelResponseV1(value=f"OpenAI request failed: {str(e)}")
