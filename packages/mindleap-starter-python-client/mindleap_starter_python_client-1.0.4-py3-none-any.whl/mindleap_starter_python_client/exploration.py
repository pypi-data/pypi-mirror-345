from uuid import uuid4

from mindleap_starter_python_client.graph_model import *


class AbstractObject(object):
    def __init__(self):
        pass

    def __str__(self):
        return json.dumps(self.to_json(), indent=2)

    def to_json(self) -> dict:
        pass

    def from_json(self, json: dict) -> None:
        pass

class Property(AbstractObject):
    def __init__(self):
        super().__init__()
        self.property_type: str | None = None
        self.property_value: AbstractPropertyValueHolder | None = None

    def to_json(self) -> dict:
        return {
            "property_type": self.property_type,
            "property_value": self.property_value.to_json()
        }

    def from_json(self, json: dict) -> None:
        self.property_type = json["property_type"]
        self.property_value = property_value_holder_from_json(json["property_value"]) if json["property_value"] else None

    def with_property_type(self, property_type: str):
        self.property_type = property_type
        return self

    def with_property_value(self, property_value: AbstractPropertyValueHolder):
        self.property_value = property_value
        return self

class Entity(AbstractObject):
    def __init__(self):
        super().__init__()
        self.id: UUID = uuid4()
        self.entity_type: str | None = None
        self.properties: list[Property] = []

    def to_json(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "entity_type": self.entity_type,
            "properties": [property.to_json() for property in self.properties]
        }

    def from_json(self, json: dict) -> None:
        self.id = UUID(json["id"]) if json["id"] else None
        self.entity_type = json["entity_type"]
        for property_json in json["properties"]:
            property: Property = Property()
            property.from_json(property_json)
            self.add_property(property)

    def with_entity_type(self, entity_type: str):
        self.entity_type = entity_type
        return self

    def add_property(self, property: Property):
        self.properties.append(property)
        return self

    def get_properties(self, property_type: str) -> list[Property]:
        result: list[Property] = []
        for property in self.properties:
            if property.property_type == property_type:
                result.append(property)
        return result

class Relation(AbstractObject):
    def __init__(self):
        super().__init__()
        self.id: UUID = uuid4()
        self.relation_type: str | None = None
        self.from_entity: Entity | None = None
        self.to_entity: Entity | None = None
        self.properties: dict[str, Property] = dict()

    def to_json(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "relation_type": self.relation_type,
            "from_entity": self.from_entity.to_json() if self.from_entity else None,
            "to_entity": self.to_entity.to_json() if self.to_entity else None,
            "properties": [property.to_json() for property in self.properties.values()],
        }

    def from_json(self, json: dict) -> None:
        self.id = UUID(json["id"]) if json["id"] else None
        self.relation_type = json["relation_type"]
        for property_json in json["properties"]:
            property: Property = Property()
            property.from_json(property_json)
            self.with_property(property)

    def with_relation_type(self, relation_type: str):
        self.relation_type = relation_type
        return self

    def with_from_entity(self, from_entity: Entity):
        self.from_entity = from_entity
        return self

    def with_to_entity(self, to_entity: Entity):
        self.to_entity = to_entity
        return self

    def with_property(self, property: Property):
        self.properties[property.property_type] = property
        return self

    def get_property(self, property_type: str) -> Property:
        return self.properties[property_type]

class Exploration(object):
    def __init__(self):
        self.id : UUID | None = None
        self.name : str | None = None
        self.graph_model: GraphModel | None = None
        self.entities : list[Entity] = []
        self.relations : list[Relation] = []

    def __str__(self):
        return json.dumps(self.to_json(), indent=2)

    def to_json(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "graph_model": self.graph_model.to_json() if self.graph_model else None,
            "entities": [entity.to_json() for entity in self.entities],
            "relations": [relation.to_json() for relation in self.relations],
        }

    def from_json(self, json: dict) -> None:
        self.id = UUID(json["id"]) if json["id"] else None
        self.name = json["name"]
        if json["graph_model"]:
            self.graph_model = GraphModel()
            self.graph_model.from_json(json["graph_model"])
        for entity_json in json["entities"]:
            entity: Entity = Entity()
            entity.from_json(entity_json)
            self.entities.append(entity)
        for relation_json in json["relations"]:
            relation: Relation = Relation()
            relation.from_json(relation_json)
            self.relations.append(relation)

    def with_id(self, id: UUID):
        self.id = id
        return self

    def with_name(self, name: str):
        self.name = name
        return self

    def with_graph_model(self, graph_model: GraphModel):
        self.graph_model = graph_model
        return self

    def add_entity(self, entity: Entity):
        self.entities.append(entity)
        return self

    def add_relation(self, relation: Relation):
        self.relations.append(relation)
        return self
