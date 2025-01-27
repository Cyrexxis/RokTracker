from pydantic import BaseModel


class GovernorData(BaseModel):
    img_path: str
    name: str
    score: int | str
