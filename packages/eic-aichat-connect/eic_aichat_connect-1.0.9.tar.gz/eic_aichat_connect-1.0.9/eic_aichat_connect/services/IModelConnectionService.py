# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_config.connect import ConnectionParams
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from eic_aichat_connect.data.version1.ModelRequestV1 import ModelRequestV1
from eic_aichat_connect.data.version1.ModelResponseV1 import ModelResponseV1

from ..connectors.IModelConnector import IModelConnector

class IModelConnectionService(ABC):

    @abstractmethod
    def create_connector(self, connection_params: ConnectionParams) -> IModelConnector:
        raise NotImplementedError("Method from interface definition")

    @abstractmethod
    def find_connector(self, connectors: list, connection_params: ConnectionParams, hash_id: Optional[str]) -> IModelConnector:
        raise NotImplementedError("Method from interface definition")

    @abstractmethod
    def find_or_create_connector(self, connectors: list, connection_params: ConnectionParams, hash_id: Optional[str]) -> tuple[IModelConnector, bool]:
        raise NotImplementedError("Method from interface definition")
    
    @abstractmethod
    def execute_request(self, connection_params: ConnectionParams, model_request: ModelRequestV1, hash_id: str = None) -> ModelResponseV1:
        raise NotImplementedError("Method from interface definition")

    # @abstractmethod
    # def get_available_models(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
    #     raise NotImplementedError("Method from interface definition")
