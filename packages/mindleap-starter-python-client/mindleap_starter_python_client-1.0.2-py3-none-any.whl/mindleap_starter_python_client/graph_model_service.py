from httpx import Response

from mindleap_starter_python_client.graph_model import *
from mindleap_starter_python_client.services import *

_GRAPH_MODEL_PATH: str = "/graph_model"
_GET_ALL_GRAPH_MODELS_METHOD: str = "/get_all_graph_models"
_GET_GRAPH_MODEL_BY_NAME_METHOD: str = "/get_graph_model_by_name"
_GET_GRAPH_MODEL_BY_ID_METHOD: str = "/get_graph_model_by_id"
_STORE_GRAPH_MODEL_METHOD: str = "/store_graph_model"
_DELETE_GRAPH_MODEL_METHOD: str = "/delete_graph_model"

class GetGraphModelByNameRequest(AbstractServiceRequest):
    def __init__(self, graph_model_name: str):
        super().__init__()
        self.graph_model_name: str = graph_model_name

    def to_json(self) -> dict:
        return {
            "graph_model_name": str(self.graph_model_name),
        }

    def from_json(self, json: dict) -> None:
        self.graph_model_name = json["graph_model_name"]

class GetGraphModelByIdRequest(AbstractServiceRequest):
    def __init__(self, graph_model_id: UUID):
        super().__init__()
        self.graph_model_id: UUID = graph_model_id

    def to_json(self) -> dict:
        return {
            "graph_model_id": str(self.graph_model_id),
        }

    def from_json(self, json: dict) -> None:
        self.graph_model_id = UUID(json["graph_model_id"])

class StoreGraphModelRequest(AbstractServiceRequest):
    def __init__(self, graph_model: GraphModel):
        super().__init__()
        self.graph_model: GraphModel = graph_model

    def to_json(self) -> dict:
        return {
            "graph_model": self.graph_model.to_json(),
        }

    def from_json(self, json: dict) -> None:
        if json["graph_model"]:
            self.graph_model = GraphModel()
            self.graph_model.from_json(json["graph_model"])

class DeleteGraphModelRequest(AbstractServiceRequest):
    def __init__(self, graph_model_id: UUID):
        super().__init__()
        self.graph_model_id: UUID = graph_model_id

    def to_json(self) -> dict:
        return {
            "graph_model_id": str(self.graph_model_id),
        }

    def from_json(self, json: dict) -> None:
        self.graph_model_id = UUID(json["graph_model_id"])

class GraphModelResponse(AbstractServiceResponse):
    def __init__(self, status: ResponseStatus | None = None, error_message: str | None = None, graph_model: GraphModel | None = None):
        super().__init__(status, error_message)
        self.graph_model: GraphModel | None = graph_model

    def to_json(self) -> dict:
        json: dict = super().to_json()
        json["graph_model"] = self.graph_model.to_json() if self.graph_model else None
        return json

    def from_json(self, json: dict) -> None:
        super().from_json(json)
        if json["graph_model"] is not None:
            self.graph_model = GraphModel()
            self.graph_model.from_json(json["graph_model"])

class GraphModelsResponse(AbstractServiceResponse):
    def __init__(self, status: ResponseStatus | None = None, error_message: str | None = None, graph_models: list[GraphModel] | None = None):
        super().__init__(status, error_message)
        self.graph_models: list[GraphModel] = graph_models if graph_models is not None else []

    def to_json(self) -> dict:
        json: dict = super().to_json()
        json["graph_models"] = [graph_model.to_json() for graph_model in self.graph_models]
        return json

    def from_json(self, json: dict) -> None:
        super().from_json(json)
        for graph_model_json in json["graph_models"]:
            graph_model: GraphModel = GraphModel()
            graph_model.from_json(graph_model_json)
            self.graph_models.append(graph_model)

class GraphModelService(AbstractService):
    def get_graph_models(self) -> list[GraphModel] | GraphModelsResponse:
        response: Response = self._httpx_client.get(
            url = self._base_url + _GRAPH_MODEL_PATH + _GET_ALL_GRAPH_MODELS_METHOD,
        )
        graph_models_response: GraphModelsResponse = GraphModelsResponse()
        graph_models_response.from_json(response.json())
        if graph_models_response.status == ResponseStatus.SUCCESS:
            return graph_models_response.graph_models
        else:
            return graph_models_response

    def get_graph_model_by_name(self, graph_model_name: str) -> GraphModel | GraphModelResponse:
        request: GetGraphModelByNameRequest = GetGraphModelByNameRequest(graph_model_name)
        response: Response = self._httpx_client.post(
            url =self._base_url + _GRAPH_MODEL_PATH + _GET_GRAPH_MODEL_BY_NAME_METHOD,
            json = request.to_json(),
        )
        graph_model_response: GraphModelResponse = GraphModelResponse()
        graph_model_response.from_json(response.json())
        if graph_model_response.status == ResponseStatus.SUCCESS:
            return graph_model_response.graph_model
        else:
            return graph_model_response

    def get_graph_model_by_id(self, graph_model_id: UUID) -> GraphModel | GraphModelResponse:
        request: GetGraphModelByIdRequest = GetGraphModelByIdRequest(graph_model_id)
        response: Response = self._httpx_client.post(
            url =self._base_url + _GRAPH_MODEL_PATH + _GET_GRAPH_MODEL_BY_ID_METHOD,
            json = request.to_json(),
        )
        graph_model_response: GraphModelResponse = GraphModelResponse()
        graph_model_response.from_json(response.json())
        if graph_model_response.status == ResponseStatus.SUCCESS:
            return graph_model_response.graph_model
        else:
            return graph_model_response

    def store_graph_model(self, graph_model: GraphModel) -> GraphModelResponse:
        if graph_model.is_valid() is False:
            raise Exception("Graph model validation failed")
        request: StoreGraphModelRequest = StoreGraphModelRequest(graph_model)
        response: Response = self._httpx_client.post(
            url =self._base_url + _GRAPH_MODEL_PATH + _STORE_GRAPH_MODEL_METHOD,
            json = request.to_json(),
        )
        graph_model_response: GraphModelResponse = GraphModelResponse()
        graph_model_response.from_json(response.json())
        return graph_model_response

    def delete_graph_model(self, graph_model_id: UUID) -> GenericResponse:
        request: DeleteGraphModelRequest = DeleteGraphModelRequest(graph_model_id)
        response: Response = self._httpx_client.post(
            url =self._base_url + _GRAPH_MODEL_PATH + _DELETE_GRAPH_MODEL_METHOD,
            json = request.to_json(),
        )
        generic_response: GenericResponse = GenericResponse()
        generic_response.from_json(response.json())
        return generic_response
