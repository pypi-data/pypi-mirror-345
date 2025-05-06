from typing import List

from pydantic import BaseModel, Field  # type: ignore


class ArticleSchema(BaseModel):
    title: str
    points: int
    by: str
    commentsURL: str


class TopArticlesSchema(BaseModel):
    top: List[ArticleSchema] = Field(..., max_length=5, description="Top 5 stories")
