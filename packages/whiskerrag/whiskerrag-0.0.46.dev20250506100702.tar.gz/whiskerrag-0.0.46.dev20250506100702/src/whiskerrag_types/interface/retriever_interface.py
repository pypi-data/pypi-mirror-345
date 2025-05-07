from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from whiskerrag_types.model.retrieval import RetrievalChunk, RetrievalConfig

T = TypeVar("T", bound=RetrievalConfig)
R = TypeVar("R", bound=RetrievalChunk)


class BaseRetriever(Generic[T, R], ABC):
    """Retriever interface."""

    @abstractmethod
    def retrieve(self, params: T) -> List[R]:
        pass
