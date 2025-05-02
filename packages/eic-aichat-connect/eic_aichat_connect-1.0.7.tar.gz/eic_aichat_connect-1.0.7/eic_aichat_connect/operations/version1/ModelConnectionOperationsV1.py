# # -*- coding: utf-8 -*-
# from pip_services4_components.config import ConfigParams
# from pip_services4_components.context import Context
# from pip_services4_components.refer import Descriptor, IReferences
# from pip_services4_config.connect import ConnectionParams
# from pip_services4_http.controller import RestOperations, RestController

# from eic_aichat_connect.data.version1.ModelRequestV1 import ModelRequestV1
# from eic_aichat_connect.services.IModelConnectionService import IModelConnectionService

# class ModelConnectionOperationsV1(RestOperations):
    
#     def __init__(self):
#         super().__init__()
#         self._modelconnection_service: IModelConnectionService = None
#         self._dependency_resolver.put("modelconnection-service", Descriptor('aichatconnect', 'service', '*', '*', '1.0'))

#         self._connectors = []
#         self._default_api = 'openai'
#         self._default_model = 'gpt-3.5-turbo-instruct'

#     def configure(self, config: ConfigParams):
#         super().configure(config)

#     def set_references(self, references: IReferences):
#         super().set_references(references)
#         self._modelconnection_service = self._dependency_resolver.get_one_required('modelconnection-service')
    
#     def _connection_params_are_valid(self, connection_params: ConnectionParams) -> tuple[bool, list]:
#         required_params = ["user", "api"]
#         missing_params = []
#         for key in required_params:
#             # Add missing key to list if null
#             if connection_params.get_as_nullable_string(key) == None: missing_params.append(key)
        
#         # Check if params are missing
#         params_are_valid = True if len(missing_params) == 0 else False
#         return params_are_valid, missing_params
    
#     def execute_request(self, connection_params: ConnectionParams, model_request: ModelRequestV1, hash_id: str = None):
#         # Check required connection params
#         params_are_valid, missing_params = self._connection_params_are_valid(connection_params)
#         if not params_are_valid:
#             return self._send_bad_request(f"ConnectionParams missing values for keys: {missing_params}")
#         try:
#             # Find or create connector
#             connector, connector_is_new = self._modelconnection_service.find_or_create_connector(self._connectors, connection_params, hash_id)
#             res = connector.execute_request(model_request)
#             # Add connector to list if new
#             if connector_is_new: self._connectors.append(connector)
#             return self._send_result(res)
#         except Exception as err:
#             return self._send_error(err)
    
#     def execute_default_request(self, connection_params: ConnectionParams, model_request: ModelRequestV1, hash_id: str = None):
#         # Set default API & model
#         connection_params.put("api", self._default_api)
#         connection_params.put("model", self._default_model)
#         return self.execute_request(connection_params, model_request, hash_id)

#     # def get_available_models(self):
#     #     context = Context.from_trace_id(self._get_trace_id())
#     #     filter_params = self._get_filter_params()
#     #     paging_params = self._get_paging_params()
#     #     try:
#     #         res = self._modelconnection_service.get_available_models(context, filter_params, paging_params)
#     #         return self._send_result(res)
#     #     except Exception as err:
#     #         return self._send_error(err)

#     # def register_routes(self, controller: RestController):
#     #     controller.register_route('get', '/available_models', None,
#     #                               self.get_available_models)
