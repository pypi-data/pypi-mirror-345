from httpx import Response

from mindleap_starter_python_client.exploration import *
from mindleap_starter_python_client.services import *

_EXPLORATION_PATH: str = "/exploration"
_GET_ALL_EXPLORATIONS_METHOD: str = "/get_all_explorations"
_GET_EXPLORATION_BY_NAME_METHOD: str = "/get_exploration_by_name"
_GET_EXPLORATION_BY_ID_METHOD: str = "/get_exploration_by_id"
_STORE_EXPLORATION_METHOD: str = "/store_exploration"
_DELETE_EXPLORATION_METHOD: str = "/delete_exploration"

class GetExplorationByNameRequest(AbstractServiceRequest):
    def __init__(self, exploration_name: str):
        super().__init__()
        self.exploration_name: str = exploration_name

    def to_json(self) -> dict:
        return {
            "exploration_name": str(self.exploration_name),
        }

    def from_json(self, json: dict) -> None:
        self.exploration_name = json["exploration_name"]

class GetExplorationByIdRequest(AbstractServiceRequest):
    def __init__(self, exploration_id: UUID):
        super().__init__()
        self.exploration_id: UUID = exploration_id

    def to_json(self) -> dict:
        return {
            "exploration_id": str(self.exploration_id),
        }

    def from_json(self, json: dict) -> None:
        self.exploration_id = UUID(json["exploration_id"])

class StoreExplorationRequest(AbstractServiceRequest):
    def __init__(self, exploration: Exploration):
        super().__init__()
        self.exploration: Exploration = exploration

    def to_json(self) -> dict:
        return {
            "exploration": self.exploration.to_json(),
        }

    def from_json(self, json: dict) -> None:
        if json["exploration"]:
            self.exploration = Exploration()
            self.exploration.from_json(json["exploration"])

class DeleteExplorationRequest(AbstractServiceRequest):
    def __init__(self, exploration_id: UUID):
        super().__init__()
        self.exploration_id: UUID = exploration_id

    def to_json(self) -> dict:
        return {
            "exploration_id": str(self.exploration_id)
        }

    def from_json(self, json: dict) -> None:
        self.exploration_id = UUID(json["exploration_id"]) if json["exploration_id"] else None

class ExplorationResponse(AbstractServiceResponse):
    def __init__(self, status: ResponseStatus | None = None, error_message: str | None = None, exploration: Exploration | None = None):
        super().__init__(status, error_message)
        self.exploration: Exploration | None = exploration

    def to_json(self) -> dict:
        json: dict = super().to_json()
        json["exploration"] = self.exploration.to_json() if self.exploration else None
        return json

    def from_json(self, json: dict) -> None:
        super().from_json(json)
        if json["exploration"] is not None:
            self.exploration = Exploration()
            self.exploration.from_json(json["exploration"])

class ExplorationsResponse(AbstractServiceResponse):
    def __init__(self, status: ResponseStatus | None = None, error_message: str | None = None, explorations: list[Exploration] | None = None):
        super().__init__(status, error_message)
        self.explorations: list[Exploration] = explorations if explorations is not None else []

    def to_json(self) -> dict:
        json: dict = super().to_json()
        json["explorations"] = [exploration.to_json() for exploration in self.explorations]
        return json

    def from_json(self, json: dict) -> None:
        super().from_json(json)
        for exploration_json in json["explorations"]:
            exploration: Exploration = Exploration()
            exploration.from_json(exploration_json)
            self.explorations.append(exploration)

class ExplorationService(AbstractService):
    def get_explorations(self) -> list[Exploration] | ExplorationsResponse:
        response: Response = self._httpx_client.get(
            url = self._base_url + _EXPLORATION_PATH + _GET_ALL_EXPLORATIONS_METHOD,
        )
        exploration_response: ExplorationsResponse = ExplorationsResponse()
        exploration_response.from_json(response.json())
        if exploration_response.status == ResponseStatus.SUCCESS:
            return exploration_response.explorations
        else:
            return exploration_response

    def get_exploration_by_name(self, exploration_name: str) -> Exploration | ExplorationResponse:
        request: GetExplorationByNameRequest = GetExplorationByNameRequest(exploration_name)
        response: Response = self._httpx_client.post(
            url =self._base_url + _EXPLORATION_PATH + _GET_EXPLORATION_BY_NAME_METHOD,
            json = request.to_json(),
        )
        exploration_response: ExplorationResponse = ExplorationResponse()
        exploration_response.from_json(response.json())
        if exploration_response.status == ResponseStatus.SUCCESS:
            return exploration_response.exploration
        else:
            return exploration_response

    def get_exploration_by_id(self, exploration_id: UUID) -> Exploration | ExplorationResponse:
        request: GetExplorationByIdRequest = GetExplorationByIdRequest(exploration_id)
        response: Response = self._httpx_client.post(
            url =self._base_url + _EXPLORATION_PATH + _GET_EXPLORATION_BY_ID_METHOD,
            json = request.to_json(),
        )
        exploration_response: ExplorationResponse = ExplorationResponse()
        exploration_response.from_json(response.json())
        if exploration_response.status == ResponseStatus.SUCCESS:
            return exploration_response.exploration
        else:
            return exploration_response

    def store_exploration(self, exploration: Exploration) -> GenericResponse:
        request: StoreExplorationRequest = StoreExplorationRequest(exploration)
        print(str(request))
        response: Response = self._httpx_client.post(
            url =self._base_url + _EXPLORATION_PATH + _STORE_EXPLORATION_METHOD,
            json = request.to_json(),
        )
        generic_response: GenericResponse = GenericResponse()
        generic_response.from_json(response.json())
        return generic_response

    def delete_exploration(self, exploration_id: UUID) -> GenericResponse:
        request: DeleteExplorationRequest = DeleteExplorationRequest(exploration_id)
        print(str(request))
        response: Response = self._httpx_client.post(
            url =self._base_url + _EXPLORATION_PATH + _DELETE_EXPLORATION_METHOD,
            json = request.to_json(),
        )
        generic_response: GenericResponse = GenericResponse()
        generic_response.from_json(response.json())
        return generic_response
