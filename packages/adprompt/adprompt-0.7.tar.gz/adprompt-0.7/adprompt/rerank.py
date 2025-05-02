from pydantic import BaseModel


class RerankScore(BaseModel):
    index: int
    score: float
