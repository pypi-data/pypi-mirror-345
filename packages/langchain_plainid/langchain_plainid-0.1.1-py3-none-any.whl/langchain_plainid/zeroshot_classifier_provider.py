import logging
from typing import List, Optional

from transformers import pipeline

from .category_classifier_provider import CategoryClassifierProvider

ALL_CATEGORIES = [
    "Weather",
    "Geography",
    "Travel",
    "News",
    "HR",
    "Finance",
    "Contracts",
    "Legal",
    "Marketing",
    "Sales",
    "Cars",
]


class ZeroShotCategoryClassifierProvider(CategoryClassifierProvider):
    """
    A zero-shot category classifier provider implementation.
    Uses Hugging Face transformers pipeline for classification.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.zeroshot_classifier = pipeline(
            "zero-shot-classification", model=model_name
        )

    def classify(self, input: str, categories: List[str]) -> Optional[str]:
        """
        Classifies the input text using zero-shot classification.

        Args:
            input (str): The input text to be classified
            categories (List[str]): List of categories to classify input into

        Returns:
            Optional[str]: The classified category name or None if classification failed
        """
        if not categories:
            logging.error("Cannot classify without categories")
            return None

        try:
            result = self.zeroshot_classifier(input, ALL_CATEGORIES, multi_label=False)

            # Extract the top category (highest score)
            top_category = result["labels"][0]

            logging.debug(
                f"Classified '{input}' as '{top_category}' with score {result['scores'][0]}"
            )
            return top_category

        except Exception as e:
            logging.error(f"Error during zero-shot classification: {str(e)}")
            return None
