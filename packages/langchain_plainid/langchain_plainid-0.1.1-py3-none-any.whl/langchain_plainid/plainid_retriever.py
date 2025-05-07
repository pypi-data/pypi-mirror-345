import logging
from typing import (
    Any,
    List,
    Optional,
    TypeVar,
)

from langchain.retrievers import SelfQueryRetriever
from langchain_core.documents import Document
from langchain_core.structured_query import (
    StructuredQuery,
)
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, Field, model_validator

from .plainid_default_query_translator import PlainIDDefaultQueryTranslator
from .plainid_filter_provider import PlainIDFilterProvider

# Module logger
logger = logging.getLogger(__name__)

# Type variable for the vector store
VST = TypeVar("VST", bound="VectorStore")


class PlainIDRetriever(SelfQueryRetriever, BaseModel):
    vectorstore: VectorStore = Field(..., description="Vector store to search")
    filter_provider: PlainIDFilterProvider = Field(
        description="Filter provider for queries"
    )
    query_constructor: Optional[Any] = Field(default=None, alias="llm_chain")
    k: int = Field(default=4, description="Number of documents to return")

    def __init__(self, **data):
        super().__init__(**data)

    @model_validator(mode="before")
    @classmethod
    def validate_translator(cls, values: dict) -> Any:
        try:
            values = SelfQueryRetriever.validate_translator(values)
        except Exception:
            values["structured_query_translator"] = PlainIDDefaultQueryTranslator()

        return values

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

        structured_query = StructuredQuery(query=query, filter=filter)
        new_query, search_kwargs = super()._prepare_query(query, structured_query)
        logger.info("using filter : %s", search_kwargs["filter"])
        docs = self._get_docs_with_query(new_query, search_kwargs)
        logger.info("Found %d relevant documents", len(docs))
        return docs
