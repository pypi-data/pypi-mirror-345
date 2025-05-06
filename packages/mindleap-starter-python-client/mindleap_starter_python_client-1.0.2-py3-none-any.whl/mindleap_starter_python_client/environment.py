from io import TextIOBase

from dotenv import dotenv_values


class AbstractEnvironmentValueProvider(object):
    def provide_value(self, key: str) -> str:
        pass

class DotEnvValueProvider(AbstractEnvironmentValueProvider):
    def __init__(self, value_stream: TextIOBase | None = None):
        self.external_values: dict[str, str] = dict() if not value_stream else dotenv_values(stream=value_stream)
        self.internal_values: dict[str, str] = dotenv_values()

    def provide_value(self, key: str) -> str | None:
        value: str | None = self.external_values.get(key)
        return value if value else self.internal_values.get(key)
