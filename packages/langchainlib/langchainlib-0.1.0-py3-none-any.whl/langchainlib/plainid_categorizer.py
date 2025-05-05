import logging
from typing import Any, Optional

from langchain_core.language_models import BaseLLM
from langchain_core.runnables import Runnable, RunnableConfig

from .plainid_permissions_provider import PlainIDPermissionsProvider


class PlainIDCategorizer(Runnable[str, str]):
    def __init__(self, llm: BaseLLM, permissions_provider: PlainIDPermissionsProvider):
        self.llm = llm
        self.permissions_provider = permissions_provider

    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        permissions = self.permissions_provider.get_permissions()
        if permissions is None:
            raise ValueError("cannot retrieve plainid permissions")

        result = self.llm.invoke(
            f"""You will classify text into one of the provided categories.
                ONLY respond with a single category name from the provided list with best match - no other words, no explanations, no prefix.
                If no category matches, respond with only "None".
                Don't come up with your own categories.
                Categories: {permissions.categories}
                Text: {input}
                Response:"""
        )

        logging.debug(f"Categorizer result: {result}")

        # Parse the response to extract only the category name
        result_cleaned = result.strip()

        # Check if result is "None", raise exception
        if result_cleaned.lower() == "none":
            raise ValueError("no category")

        # Create a lowercase mapping of categories for case-insensitive matching
        categories_map = {
            category.lower(): category for category in permissions.categories
        }

        # Split the response into words and iterate backwards
        words = result_cleaned.split()
        for word in reversed(words):
            # Check each word (lowercase) against categories
            word_lower = word.lower()
            if word_lower in categories_map:
                # Return the original case from the categories list
                return categories_map[word_lower]

        # If we reach here, no category was found - raise exception
        raise ValueError("no category")

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
