import logging
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import (
    OperatorConfig,
)

from .plainid_permissions_provider import PlainIDPermissionsProvider


class PlainIDAnonymizer(Runnable[str, str]):
    def __init__(
        self,
        permissions_provider: PlainIDPermissionsProvider,
        encrypt_key: Optional[str] = None,
    ):
        if encrypt_key is not None:
            self.encrypt_key = encrypt_key
        self.permissions_provider = permissions_provider

    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        permissions = self.permissions_provider.get_permissions()
        if permissions is None:
            raise ValueError("No permissions found for the user.")

        # Get entities to mask and entities to encode
        mask_entities, encode_entities = (
            self.permissions_provider.get_entities_by_action(permissions.entities)
        )

        # If no entities to process, return original input
        if not mask_entities and not encode_entities:
            return input

        analyzer = AnalyzerEngine()

        # Initial analysis for all entities
        analyzer_results = analyzer.analyze(
            text=input, entities=mask_entities + encode_entities, language="en"
        )
        if not analyzer_results:
            return input

        operators = {"DEFAULT": OperatorConfig("replace", {"new_value": "***"})}

        # Configure encrypt operator for encode entities
        if hasattr(self, "encrypt_key"):
            for entity in encode_entities:
                if entity not in mask_entities:
                    operators[entity] = OperatorConfig(
                        "encrypt", {"key": self.encrypt_key}
                    )

        # Configure mask operator for mask entities (these have priority over encrypt)
        for entity in mask_entities:
            operators[entity] = OperatorConfig("replace", {"new_value": "***"})

        anonymizer = AnonymizerEngine()
        anonymized_result = anonymizer.anonymize(
            text=input, analyzer_results=analyzer_results, operators=operators
        )

        logging.debug(f"anonymized input to {anonymized_result.text}")
        return anonymized_result.text

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
