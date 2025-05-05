import logging
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Union,
)

from .plainid_client import PlainIDClient

# Configure module logger
logger = logging.getLogger(__name__)


class PlainIDFilterProvider:
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        """
        Initialize PlainIDFilterProvider with authentication credentials.

        Args:
                base_url (str): Base URL for PlainID service
                client_id (str): Client ID for authentication
                client_secret (str): Client secret for authentication
        """
        self.client = PlainIDClient(base_url, client_id, client_secret)

    def get_filter(self) -> Optional[Union[Callable, Dict[str, Any]]]:
        """
        Returns a PlainID filter string that can be used to filter the documents in the vector store.

        Returns:
                Optional[Union[Callable, Dict[str, Any]]]: Filter data from PlainID
        """
        resolution = self.client.get_resolution()
        if resolution is None:
            return None

        faiss_filter = self._map_plainid_resoulution_to_filter(resolution)
        logger.debug("filter: %s", faiss_filter)

        return faiss_filter

    def _map_plainid_resoulution_to_filter(
        self, resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Converts a PlainID resolution response to a FAISS filter format.

        Supports the following operations:
        - $eq (equals)
        - $neq (not equals)
        - $gt (greater than)
        - $lt (less than)
        - $gte (greater than or equal)
        - $lte (less than or equal)
        - $in (membership in list)
        - $nin (not in list)
        - $and (all conditions must match)
        - $or (any condition must match)
        - $not (negation of condition)

        Args:
                resolution (Dict[str, Any]): The PlainID resolution response

        Returns:
                Dict[str, Any]: The FAISS filter dictionary
        """
        if not resolution or "response" not in resolution:
            logger.warning("Invalid resolution format - missing 'response' field")
            return {}

        try:
            # Navigate to the asset-attributes-filter section
            responses = resolution.get("response", [])
            if not responses:
                return {}

            privileges = responses[0].get("privileges", {})
            allowed = privileges.get("allowed", [])

            if not allowed:
                return {}

            actions = allowed[0].get("actions", [])
            if not actions:
                return {}

            asset_attributes_filter = actions[0].get("asset-attributes-filter", {})
            if not asset_attributes_filter:
                return {}

            # Convert the filter structure
            return self._convert_plainid_filter(asset_attributes_filter)
        except Exception as e:
            logger.error(f"Error mapping PlainID filter: {str(e)}")
            return {}

    def _convert_plainid_filter(self, filter_part: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively converts a part of the PlainID filter structure to FAISS filter format.

        Args:
                filter_part (Dict[str, Any]): A part of the PlainID filter structure

        Returns:
                Dict[str, Any]: The corresponding FAISS filter part
        """
        result = {}

        # Handle AND conditions
        if "AND" in filter_part:
            and_conditions = filter_part["AND"]
            converted_conditions = []
            for condition in and_conditions:
                converted = self._convert_condition(condition)
                if converted:  # Only add non-empty conditions
                    converted_conditions.append(converted)

            if converted_conditions:
                result["$and"] = converted_conditions

        # Handle OR conditions
        elif "OR" in filter_part:
            or_conditions = filter_part["OR"]
            converted_conditions = []
            for condition in or_conditions:
                converted = self._convert_plainid_filter(condition)
                if converted:  # Only add non-empty conditions
                    converted_conditions.append(converted)

            if converted_conditions:
                result["$or"] = converted_conditions

        return result

    def _convert_condition(self, condition: Dict[str, Any]) -> Dict[str, Any]:
        attribute = condition.get("attribute")
        operator = condition.get("operator")
        values = condition.get("values", [])

        if not attribute or not operator:
            return {}

        # Map PlainID operators to FAISS operators
        operator_mapping = {
            "EQUALS": "$eq",
            "NOTEQUALS": "$neq",
            "NOT_EQUALS": "$neq",
            "GREATER": "$gt",
            "GREATE": "$gt",  # Handle misspelling in the PlainID response
            "GREAT_EQUALS": "$gte",
            "GREATER_EQUALS": "$gte",
            "LESS": "$lt",
            "LESS_EQUALS": "$lte",
            "IN": "$in",
            "NOT_IN": "$nin",
        }

        # Unsupported pattern matching operators in FAISS
        unsupported_operators = ["CONTAINS", "STARTWITH", "ENDWITH"]

        if operator in operator_mapping:
            faiss_operator = operator_mapping[operator]

            # Handle type conversion for numeric values
            if condition.get("type") == "NUMERIC":
                values = [
                    float(val) if val.replace(".", "", 1).isdigit() else val
                    for val in values
                ]

            # For single-value operators
            if (
                faiss_operator in ["$eq", "$neq", "$gt", "$lt", "$gte", "$lte"]
                and values
            ):
                return {attribute: {faiss_operator: values[0]}}

            # For multi-value operators
            if faiss_operator in ["$in", "$nin"]:
                return {attribute: {faiss_operator: values}}

        elif operator in unsupported_operators:
            logger.warning(
                f"Operator '{operator}' is not supported by FAISS, skipping this condition"
            )
            return {}
        else:
            logger.warning(f"Unknown operator: {operator}")
            return {}

        return {}
