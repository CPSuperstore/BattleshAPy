class PlayerShip:
    def __init__(self, id: str):
        self.id = id
        self.target_x = None
        self.target_y = None

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            target_x=self.target_x,
            target_y=self.target_y
        )

    @classmethod
    def from_dict(cls, data: dict):
        c = cls(data["id"])
        c.target_x = data["target_x"]
        c.target_y = data["target_y"]

        return c
