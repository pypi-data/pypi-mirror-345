import logging
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig

from .category_classifier_provider import CategoryClassifierProvider
from .plainid_permissions_provider import PlainIDPermissionsProvider


class PlainIDCategorizer(Runnable[str, str]):
    def __init__(
        self,
        classifier_provider: CategoryClassifierProvider,
        permissions_provider: PlainIDPermissionsProvider,
    ):
        self.classifier_provider = classifier_provider
        self.permissions_provider = permissions_provider

    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        permissions = self.permissions_provider.get_permissions()
        if permissions is None or not permissions.categories:
            raise ValueError("Failed to retrieve categories from permissions provider")

        category = self.classifier_provider.classify(
            input, categories=permissions.categories
        )

        if category is None:
            raise ValueError("Couldn't classify input into a valid category")

        logging.debug(f"Categorizer result: {category}")
        return category

    async def ainvoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        """Asynchronously process a single string input."""
        import asyncio
        from functools import partial

        # Use run_in_executor to run invoke method in a separate thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(self.invoke, input, config, **kwargs)
        )
