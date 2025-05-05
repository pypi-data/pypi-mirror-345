import logging
from typing import (
    List,
    TypeVar,
)

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, Field

from .plainid_filter_provider import PlainIDFilterProvider

# Module logger
logger = logging.getLogger(__name__)

# Type variable for the vector store
VST = TypeVar("VST", bound="VectorStore")


class PlainIDRetriever(BaseRetriever, BaseModel):
    vector_store: VectorStore = Field(description="Vector store to search")
    filter_provider: PlainIDFilterProvider = Field(
        description="Filter provider for queries"
    )
    k: int = Field(default=4, description="Number of documents to return")

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug("Initialized PlainIDRetriever with k=%d", self.k)

    def _get_relevant_documents(
        self, query: str, *, run_manager=None
    ) -> List[Document]:
        """
        Get documents relevant to the query.

        Args:
                query: String to find relevant documents for
                run_manager: Optional run manager for callbacks

        Returns:
                List of relevant documents
        """
        logger.info("Getting relevant documents for query: %s", query)
        filter = self.filter_provider.get_filter()
        logger.debug("Using filter: %s", filter)

        documents = self.vector_store.similarity_search(query, k=self.k, filter=filter)
        logger.info("Found %d relevant documents", len(documents))

        return documents
