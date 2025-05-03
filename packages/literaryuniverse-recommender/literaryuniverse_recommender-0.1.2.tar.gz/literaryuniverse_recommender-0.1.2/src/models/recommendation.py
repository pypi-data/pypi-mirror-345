from typing import List
from pydantic import BaseModel
from uuid import UUID


class Recommendation(BaseModel):
    storyId: UUID
    title: str
    genres: List[str]
    language: str
    ageRating: str
