from enum import StrEnum

from pydantic import BaseModel


class BatchType(StrEnum):
    ALLIANCE = "Alliance"
    HONOR = "Honor"
    SEED = "Seed"


class BatchStatus(BaseModel):
    type: BatchType
