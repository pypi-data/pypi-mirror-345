from uuid import UUID

from mindleap_starter_python_client.data_types import *


# The most abstract model for object types
class AbstractObjectModel(object):
    def __init__(self):
        self.type_name: str | None = None
        self.type_label: str | None = None

    def __str__(self):
        return json.dumps(self.to_json(), indent=2)

    def to_json(self) -> dict:
        return {
            "type_name": self.type_name,
            "type_label": self.type_label,
        }

    def from_json(self, json: dict) -> None:
        self.type_name = json["type_name"]
        self.type_label = json["type_label"]

    def with_type_name(self, type_name: str):
        self.type_name = type_name
        return self

    def with_type_label(self, type_label: str):
        self.type_label = type_label
        return self

    def is_valid(self) -> bool:
        if self.type_name is None or len(self.type_name) == 0:
            return False
        if self.type_label is None or len(self.type_label) == 0:
            return False
        return True

# A model for a property type (on an entity or relation type)
class PropertyModel(AbstractObjectModel):
    def __init__(self):
        super().__init__()
        self.value_type: PropertyValueType | None = None

    def to_json(self) -> dict:
        json: dict = super().to_json()
        json["value_type"] = self.value_type
        return json

    def from_json(self, json: dict) -> None:
        super().from_json(json)
        self.value_type = json["value_type"]

    def is_valid(self) -> bool:
        if super().is_valid() is False:
            return False
        if self.value_type is None:
            return False
        return True

    def with_value_type(self, value_type: PropertyValueType):
        self.value_type = value_type
        return self

# A model for an entity type
class EntityModel(AbstractObjectModel):
    def __init__(self):
        super().__init__()
        self.use_avatar_icon: bool = False
        self.icon_type: IconType | None = None
        self.property_models: dict[str, PropertyModel] = dict()
        self.labelling_property_types: list[str] = []

    def to_json(self) -> dict:
        json: dict = super().to_json()
        json["use_avatar_icon"] = self.use_avatar_icon
        json["icon_type"] = self.icon_type
        json["property_models"] = [property_model.to_json() for property_model in self.property_models.values()]
        json["labelling_property_types"] = self.labelling_property_types
        return json

    def from_json(self, json: dict) -> None:
        super().from_json(json)
        self.use_avatar_icon = json["use_avatar_icon"]
        self.icon_type = json["icon_type"]
        for property_model_json in json["property_models"]:
            property_model: PropertyModel = PropertyModel()
            property_model.from_json(property_model_json)
            self.add_property_model(property_model)
        for labelling_property_type in json["labelling_property_types"]:
            self.add_labelling_property_type(labelling_property_type)

    def is_valid(self) -> bool:
        if super().is_valid() is False:
            return False
        if self.use_avatar_icon is False and self.icon_type is None:
            return False
        if len(self.property_models) == 0:
            return False
        for property_model in self.property_models.values():
            if property_model.is_valid() is False:
                return False
        if len(self.labelling_property_types) == 0:
            return False
        return True

    def with_use_avatar_icon(self, use_avatar_icon: bool = True):
        self.use_avatar_icon = use_avatar_icon
        if use_avatar_icon is True:
            self.icon_type = None
        return self

    def with_icon_type(self, icon_type: str):
        self.icon_type = icon_type
        if icon_type is not None:
            self.use_avatar_icon = False
        return self

    def add_property_model(self, property_model: PropertyModel):
        self.property_models[property_model.type_name] = property_model
        return self

    def get_property_model(self, property_type: str) -> PropertyModel | None:
        return self.property_models[property_type]

    def add_labelling_property_type(self, property_type: str):
        if property_type not in self.property_models:
            raise Exception("Labelling property type must be among property_models")
        self.labelling_property_types.append(property_type)
        return self

    def with_labelling_property_types(self, property_types: list[str]):
        for property_type in property_types:
            self.labelling_property_types.append(property_type)
        return self

# A model for a relation type (between two entity types)
class RelationModel(AbstractObjectModel):
    def __init__(self):
        super().__init__()
        self.directed: bool = False
        self.from_entity_type: str | None = None
        self.to_entity_type: str | None = None
        self.property_models: dict[str, PropertyModel] = dict()
        self.labelling_property_types: list[str] = []

    def to_json(self) -> dict:
        json: dict = super().to_json()
        json["directed"] = self.directed
        json["from_entity_type"] = self.from_entity_type
        json["to_entity_type"] = self.to_entity_type
        json["property_models"] = [property_model.to_json() for property_model in self.property_models.values()]
        json["labelling_property_types"] = self.labelling_property_types
        return json

    def from_json(self, json: dict) -> None:
        super().from_json(json)
        self.directed = json["directed"]
        self.from_entity_type = json["from_entity_type"]
        self.to_entity_type = json["to_entity_type"]
        for property_model_json in json["property_models"]:
            property_model = PropertyModel()
            property_model.from_json(property_model_json)
            self.add_property_model(property_model)
        for labelling_property_type in json["labelling_property_types"]:
            self.add_labelling_property_type(labelling_property_type)

    def is_valid(self) -> bool:
        if super().is_valid() is False:
            return False
        if self.from_entity_type is None:
            return False
        if self.to_entity_type is None:
            return False
        for property_model in self.property_models.values():
            if property_model.is_valid() is False:
                return False
        return True

    def add_property_model(self, property_model: PropertyModel):
        self.property_models[property_model.type_name] = property_model
        return self

    def get_property_model(self, property_type_name: str) -> PropertyModel | None:
        return self.property_models[property_type_name]

    def add_labelling_property_type(self, property_type_name: str):
        if property_type_name not in self.property_models:
            raise Exception("Labelling property type must be among property_models")
        self.labelling_property_types.append(property_type_name)
        return self

    def with_labelling_property_types(self, property_types: list[str]):
        for property_type in property_types:
            self.add_labelling_property_type(property_type)
        return self

    def with_directed(self, directed: bool):
        self.directed = directed
        return self

    def with_from_entity_type(self, from_entity_type_name: str):
        self.from_entity_type = from_entity_type_name
        return self

    def with_to_entity_type(self, to_entity_type_name: str):
        self.to_entity_type = to_entity_type_name
        return self


# Represents a graph model and contains:
# - Supported entity models
# - Supported relation models
class GraphModel(object):
    def __init__(self, id: UUID | None = None):
        self.id: UUID = id
        self.name: str | None = None
        self.entity_models: dict[str, EntityModel] = dict()
        self.relation_models: dict[str, RelationModel] = dict()

    def __str__(self):
        return json.dumps(self.to_json(), indent=2)

    def to_json(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "entity_models": [entity_model.to_json() for entity_model in self.entity_models.values()],
            "relation_models": [relation_model.to_json() for relation_model in self.relation_models.values()],
        }

    def from_json(self, json: dict) -> None:
        self.id = UUID(json["id"]) if json["id"] else None
        self.name = json["name"]
        for entity_model_json in json["entity_models"]:
            entity_model: EntityModel = EntityModel()
            entity_model.from_json(entity_model_json)
            self.add_entity_model(entity_model)
        for relation_model_json in json["relation_models"]:
            relation_model: RelationModel = RelationModel()
            relation_model.from_json(relation_model_json)
            self.add_relation_model(relation_model)

    def with_id(self, id: UUID):
        self.id = id
        return self

    def with_name(self, name: str):
        self.name = name
        return self

    def add_entity_model(self, entity_model: EntityModel):
        self.entity_models[entity_model.type_name] = entity_model
        return self

    def get_entity_model(self, entity_type_name: str) -> [EntityModel | None]:
        return self.entity_models[entity_type_name]

    def add_relation_model(self, relation_model: RelationModel):
        self.relation_models[relation_model.type_name] = relation_model
        return self

    def get_relation_model(self, relation_type_name: str) -> [RelationModel | None]:
        return self.relation_models[relation_type_name]

    def is_valid(self) -> bool:
        if self.id is None:
            return False
        if self.name is None or len(self.name) == 0:
            return False
        if len(self.entity_models) == 0:
            return False
        for entity_model in self.entity_models.values():
            if entity_model.is_valid() is False:
                return False
        for relation_model in self.relation_models.values():
            if relation_model.is_valid() is False:
                return False
        return True
