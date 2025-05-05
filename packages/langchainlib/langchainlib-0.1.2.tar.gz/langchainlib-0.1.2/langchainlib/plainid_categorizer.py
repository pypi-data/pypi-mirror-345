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
                Don't come up with your own categories. If there is no best match, respond with "None".
                If you cannot classify the text's category, respond with "None".
                Text: {input}
                Categories: {permissions.categories}
                Response:"""
        )

        logging.debug(f"detected category: {result}")
        result_cleaned = result.strip()
        if result_cleaned.lower() == "none":
            raise ValueError(f"allowed categories are : {permissions.categories}")

        categories_map = {
            category.lower(): category for category in permissions.categories
        }

        words = result_cleaned.split()
        for word in reversed(words):
            word_lower = word.lower()
            if word_lower in categories_map:
                return input

        raise ValueError(f"allowed categories are : {permissions.categories}")

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
