import json


class NotSet:
    pass


class PlayerShip:
    def __init__(self, id: str):
        self.id = id
        self.target_x = None
        self.target_y = None
        self.metadata = {}

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            target_x=self.target_x,
            target_y=self.target_y,
            metadata=self.metadata
        )

    @classmethod
    def from_dict(cls, data: dict):
        c = cls(data["id"])
        c.target_x = data["target_x"]
        c.target_y = data["target_y"]
        c.metadata = data.get("metadata", {})

        return c

    def set_attribute(self, attribute: str, value):
        try:
            json.dumps(value)
        except(TypeError, OverflowError):
            raise ValueError("Attribute values MUST be serializable!")

        self.metadata[attribute] = value

    def get_attribute(self, attribute: str, default=NotSet):
        if default == NotSet:
            if attribute not in self.metadata:
                raise AttributeError("Ship does not have attribute '{}'!".format(attribute))

            return self.metadata.get(attribute)
        else:
            return self.metadata.get(attribute, default)
