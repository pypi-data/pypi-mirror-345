# -*- coding: utf-8 -*-
from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable
from pip_services4_config.connect import ConnectionParams
from pip_services4_data.query import FilterParams, PagingParams, DataPage

from eic_aichat_connect.data.version1.ModelResponseV1 import ModelResponseV1

from ..connectors.IModelConnector import IModelConnector
from ..connectors.MockModelConnector import MockModelConnector
from ..connectors.AnthropicModelConnector import AnthropicModelConnector
from ..connectors.DeepSeekModelConnector import DeepSeekModelConnector
from ..connectors.OpenAIModelConnector import OpenAIModelConnector
from ..connectors.PerplexityModelConnector import PerplexityModelConnector
from ..data.version1.ModelRequestV1 import ModelRequestV1
from .IModelConnectionService import IModelConnectionService

class ModelConnectionService(IModelConnectionService, IConfigurable, IReferenceable):

    def __init__(self):
        self._connectors = []
        self._default_api = 'openai'
        self._default_model = 'gpt-3.5-turbo-instruct'

    def configure(self, config: ConfigParams):
        super().configure(config)

    def set_references(self, references: IReferences):
        super().set_references(references)

    def _hash_connection_params(self, connection_params: ConnectionParams) -> str:
        return str(hash(connection_params.to_string()))
    
    def _connection_params_are_valid(self, connection_params: ConnectionParams) -> tuple[bool, list]:
        required_params = ["user", "api"]
        missing_params = []
        for key in required_params:
            if connection_params.get_as_nullable_string(key) is None:
                missing_params.append(key)
        params_are_valid = len(missing_params) == 0
        return params_are_valid, missing_params
    
    def create_connector(self, connection_params: ConnectionParams) -> IModelConnector:
        connectors_by_API = {
            "mock": MockModelConnector,
            "anthropic": AnthropicModelConnector,
            "deepseek": DeepSeekModelConnector,
            "openai": OpenAIModelConnector,
            "perplexity": PerplexityModelConnector
        }

        api = connection_params.get_as_nullable_string("api").lower()
        if not api in connectors_by_API: raise KeyError(f"API {api} not found")

        connector = connectors_by_API[api](connection_params)
        return connector

    ## TODO: how to handle `not hash_id == hash_params`?
    def find_connector(self, connectors: list, connection_params: ConnectionParams, hash_id: str = None) -> IModelConnector:
        if not hash_id == None:
            for connector in connectors:
                if connector.hash_id == hash_id: return connector

        hash_params = self._hash_connection_params(connection_params)
        for connector in connectors:
            if connector.hash_id == hash_params: return connector

        return None

    def find_or_create_connector(self, connectors: list, connection_params: ConnectionParams, hash_id: str = None) -> tuple[IModelConnector, bool]:
        connector = self.find_connector(connectors, connection_params, hash_id)
        connector_is_new = False

        if connector == None:
            connector = self.create_connector(connection_params)
            connector_is_new = True

        return connector, connector_is_new
    
    def execute_request(self, connection_params: ConnectionParams, model_request: ModelRequestV1, hash_id: str = None) -> ModelResponseV1:
        params_are_valid, missing_params = self._connection_params_are_valid(connection_params)
        if not params_are_valid:
            return {'error': 'missing params', 'missing': missing_params}

        connector, connector_is_new = self.find_or_create_connector(
            self._connectors, connection_params, hash_id
        )
        result = connector.execute_request(model_request)

        if connector_is_new:
            self._connectors.append(connector)

        return result

    # def get_available_models(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
    #     return list(map(lambda m: m.value, ModelTypesV1))
