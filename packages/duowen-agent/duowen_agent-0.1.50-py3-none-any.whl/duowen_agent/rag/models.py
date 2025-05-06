from typing import Optional, List

from pydantic import BaseModel, Field, computed_field


class Document(BaseModel):
    """Class for storing a piece of text and associated metadata."""

    page_content: str

    vector_content: Optional[str] = None

    vector: Optional[list[float]] = None

    metadata: Optional[dict] = Field(default_factory=dict)

    kb_id: Optional[List[str]] = None

    kb: Optional[List[str]] = None

    label: Optional[List[str]] = None

    id: Optional[str] = None

    content_split: Optional[str] = None

    create_time: Optional[str] = None

    title: Optional[str] = None

    slots: Optional[List[str]] = None

    question: Optional[List[str]] = None

    institution: Optional[List[str]] = None

    authors: Optional[List[str]] = None

    abstract: Optional[str] = None

    file_id: Optional[str] = None

    chunk_index: Optional[int] = None

    def __hash__(self):
        return hash(self.page_content)

    def __eq__(self, other):
        if isinstance(other, Document):
            return self.page_content == other.page_content
        return False


class SearchResult(BaseModel):
    result: Document
    token_similarity_score: Optional[float] = None
    vector_similarity_score: Optional[float] = None
    hybrid_similarity_score: Optional[float] = None
    rerank_similarity_score: Optional[float] = None

    @computed_field
    def similarity_score(self) -> float:
        return (
            self.rerank_similarity_score
            or self.hybrid_similarity_score
            or self.vector_similarity_score
            or self.token_similarity_score
        )
