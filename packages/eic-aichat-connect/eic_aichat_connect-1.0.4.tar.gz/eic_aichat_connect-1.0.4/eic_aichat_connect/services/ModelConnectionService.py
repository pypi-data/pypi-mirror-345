# -*- coding: utf-8 -*-
from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable
from pip_services4_config.connect import ConnectionParams
from pip_services4_data.query import FilterParams, PagingParams, DataPage

from ..connectors.IModelConnector import IModelConnector
from ..connectors.MockModelConnector import MockModelConnector
from ..connectors.AnthropicModelConnector import AnthropicModelConnector
from ..connectors.DeepSeekModelConnector import DeepSeekModelConnector
from ..connectors.OpenAIModelConnector import OpenAIModelConnector
from ..connectors.PerplexityModelConnector import PerplexityModelConnector
from ..data.version1.ModelTypesV1 import ModelTypesV1
from .IModelConnectionService import IModelConnectionService

class ModelConnectionService(IModelConnectionService, IConfigurable, IReferenceable):

    def configure(self, config: ConfigParams):
        pass

    def set_references(self, references: IReferences):
        pass

    def _hash_connection_params(self, connection_params: ConnectionParams) -> str:
        return str(hash(connection_params.to_string()))
    
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

    # def get_available_models(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
    #     return list(map(lambda m: m.value, ModelTypesV1))
