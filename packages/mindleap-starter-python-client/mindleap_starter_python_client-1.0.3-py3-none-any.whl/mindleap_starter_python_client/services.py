import json
from enum import StrEnum

from httpx import Client

from mindleap_starter_python_client.environment import *

_MINDLEAP_BASE_PATH: str = "/api/v3/mindleap"

class ServiceKey(StrEnum):
    MINDLEAP_STARTER_HOST_URL = "MINDLEAP_STARTER_HOST_URL"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"

class ResponseStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class AbstractServiceRequest(object):
    def __init__(self):
        pass

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self) -> dict:
        pass

    def from_json(self, json: dict) -> None:
        pass

class AbstractServiceResponse(object):
    def __init__(self, status: ResponseStatus | None = None, error_message: str | None = None):
        self.status: ResponseStatus | None = status
        self.error_message: str | None = error_message

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self) -> dict:
        return {
            "status": self.status,
            "error_message": self.error_message,
        }

    def from_json(self, json: dict) -> None:
        self.status = json["status"]
        self.error_message = json["error_message"]

class GenericResponse(AbstractServiceResponse):
    pass

class AbstractService(object):
    def __init__(self, value_provider: AbstractEnvironmentValueProvider | None = None):
        if value_provider is None:
            value_provider = DotEnvValueProvider(None)
        self._value_provider: AbstractEnvironmentValueProvider = value_provider
        self._base_url: str = self._value_provider.provide_value(ServiceKey.MINDLEAP_STARTER_HOST_URL) + _MINDLEAP_BASE_PATH
        self._request_timeout: str | None = self._value_provider.provide_value(ServiceKey.REQUEST_TIMEOUT)
        self._httpx_client: Client = Client(timeout = float(self._request_timeout) if self._request_timeout else None)
