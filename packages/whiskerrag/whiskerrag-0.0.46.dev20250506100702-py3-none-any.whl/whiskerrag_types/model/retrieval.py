from typing import List, Optional, Union

from deprecated import deprecated
from pydantic import BaseModel, Field, field_serializer

from whiskerrag_types.model.chunk import Chunk
from whiskerrag_types.model.knowledge import EmbeddingModelEnum


class RetrievalBaseConfig(BaseModel):
    embedding_model_name: Union[EmbeddingModelEnum, str] = Field(
        ..., description="The name of the embedding model"
    )
    similarity_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="The similarity threshold, ranging from 0.0 to 1.0.",
    )
    top: int = Field(1024, ge=1, description="The maximum number of results to return.")
    metadata_filter: dict = Field({}, description="metadata filter")

    @field_serializer("embedding_model_name")
    def serialize_embedding_model_name(
        self, embedding_model_name: Optional[Union[EmbeddingModelEnum, str]]
    ) -> Optional[str]:
        if embedding_model_name:
            if isinstance(embedding_model_name, EmbeddingModelEnum):
                return embedding_model_name.value
            else:
                return embedding_model_name
        else:
            return None


class QueryBySpaceConfig(RetrievalBaseConfig):
    type: str = Field(
        "query_in_space_list",
        description="The type of the request, should be 'query_in_space_list'.",
    )
    space_id_list: List[str] = Field(..., description="space id list")


class QueryByKnowledgeConfig(RetrievalBaseConfig):
    type: str = Field(
        "query_in_knowledge_list",
        description="The type of the request, should be 'query_in_knowledge_list'.",
    )
    embedding_model_name: str = Field(
        ..., description="The name of the embedding model"
    )
    space_id_list: List[str] = Field(..., description="knowledge id list")


class QueryByDeepRetrieval(RetrievalBaseConfig):
    type: str = Field(
        "deep_retrieval",
        description="The type of the request, should be 'deep_retrieval'.",
    )
    space_name_list: List[str] = Field(..., description="space name list")


RetrievalConfig = Union[
    QueryBySpaceConfig, QueryByKnowledgeConfig, QueryByDeepRetrieval, dict
]


@deprecated(
    "RetrievalBySpaceRequest is deprecated, please use RetrievalRequest instead."
)
class RetrievalBySpaceRequest(RetrievalBaseConfig):
    question: str = Field(..., description="The query question")
    space_id_list: List[str] = Field(..., description="space id list")


@deprecated(
    "RetrievalBySpaceRequest is deprecated, please use RetrievalRequest instead."
)
class RetrievalByKnowledgeRequest(RetrievalBaseConfig):
    question: str = Field(..., description="The query question")
    knowledge_id_list: List[str] = Field(..., description="knowledge id list")


class RetrievalRequest(BaseModel):
    question: str = Field(..., description="The query question")
    config: RetrievalConfig = Field(
        ..., description="The configuration for the retrieval request"
    )


class RetrievalChunk(Chunk):
    similarity: float = Field(
        ..., description="The similarity of the chunk, ranging from 0.0 to 1.0."
    )
