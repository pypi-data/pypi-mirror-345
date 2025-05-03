import requests
import pandas as pd
from typing import Union, Literal, Any, Tuple, List, Dict
import warnings
from .schemas.interfaces import MappingItem
from brynq_sdk_functions import Functions

class MappingNotFoundError(Exception):
    """Raised when a requested mapping is not found"""
    pass

class Mappings:
    """
    Handles all mapping-related operations for BrynQ SDK.
    """
    def __init__(self, brynq_instance):
        """
        Initialize Mappings manager.

        Args:
            brynq_instance: The parent BrynQ instance
        """
        self._brynq = brynq_instance

    def _get_mappings(self, interface_id: int) -> List[Dict[str, Any]]:
        """Get all mappings for an interface.

        Args:
            interface_id (int): The ID of the interface

        Returns:
            List[Dict[str, Any]]: List of mapping configurations

        Raises:
            ValueError: If interface_id is not a positive integer or if the response data is invalid
            requests.exceptions.RequestException: If the API request fails
        """
        # Basic validation
        if not isinstance(interface_id, int) or interface_id <= 0:
            raise ValueError("interface_id must be a positive integer")

        response = self._brynq.session.get(
            f"{self._brynq.url}interfaces/{interface_id}/config/mapping"
        )
        response.raise_for_status()

        try:
            mappings_data = response.json()
            valid_data, _ = Functions.validate_pydantic_data(mappings_data, schema=MappingItem)
            return valid_data
        except ValueError as e:
            raise ValueError(f"Invalid mappings data: {str(e)}")

    def _to_dataframe(self, mapping_data: dict, prefix: bool = False) -> pd.DataFrame:
        """Convert mapping values to DataFrame format"""
        rows = []
        for value in mapping_data['values']:
            row = {}
            for key, val in value['input'].items():
                row[f'input.{key}' if prefix else key] = val
            for key, val in value['output'].items():
                row[f'output.{key}' if prefix else key] = val
            rows.append(row)
        return pd.DataFrame(rows)

    def _to_dict(self, mapping_data: dict) -> dict:
        """Convert mapping values to dictionary format"""
        mappings = {}
        for value in mapping_data['values']:
            input_key = ','.join(value['input'].values())
            output_value = ','.join(value['output'].values()) if len(value['output']) > 1 else next(iter(value['output'].values()))
            mappings[input_key] = output_value
        return mappings

    def get(self, interface_id: int, mapping: str, as_df: bool = False, prefix: bool = False) -> dict:
        """Get the mapping from BrynQ.

        Args:
            interface_id (int): The id of the task in BrynQ
            mapping (str): The name of the mapping
            as_df (bool, optional): If True, returns mappings as pandas DataFrame. If False, returns mappings as dictionary. Defaults to False.
            prefix (bool, optional): Only used when as_df is True. If True, prefixes column names with 'input.' and 'output.'. Defaults to False.

        Returns:
            dict: Dictionary with keys:
                - 'default_value': The default value for the mapping
                - 'mappings': Either a DataFrame (if as_df=True) or a dictionary (if as_df=False)

        Raises:
            MappingNotFoundError: If mapping is not found
            ValueError: If mapping data is invalid
        """
        mappings = self._get_mappings(interface_id=interface_id)
        mapping_data = next((item for item in mappings if item['name'] == mapping), None)

        if not mapping_data:
            raise MappingNotFoundError(f"Mapping named '{mapping}' not found")

        return {
            'default_value': mapping_data['default_value'],
            'mappings': self._to_dataframe(mapping_data, prefix) if as_df else self._to_dict(mapping_data)
        }
