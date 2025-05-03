from typing import Dict, List, Any, Optional
from .credentials import Credentials
from .mappings import Mappings
from .schemas.interfaces import Interface, InterfaceDetail, InterfaceConfig, Schedule, Scope, DevSettings
from brynq_sdk_functions import Functions

class Interfaces:
    """
    Handles all interface-related operations for BrynQ SDK.
    """
    def __init__(self, brynq_instance):
        """
        Initialize Interfaces manager.
        
        Args:
            brynq_instance: The parent BrynQ instance
        """
        self._brynq = brynq_instance
        self.credentials = Credentials(brynq_instance)
        self.mappings = Mappings(brynq_instance)

    def get(self) -> List[Dict[str, Any]]:
        """Get all interfaces this token has access to.
        
        Returns:
            List[Dict[str, Any]]: List of interfaces with their details including:
                - id (int): Interface ID
                - name (str): Interface name
                - description (str): Interface description
                - sourceSystems (List[int]): List of source system IDs
                - targetSystems (List[int]): List of target system IDs
                - taskSchedule (Dict): Task schedule details including status, timing, etc.
            
        Raises:
            ValueError: If the response data is invalid
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._brynq.session.get(
            f"{self._brynq.url}interfaces"
        )
        response.raise_for_status()
        
        try:
            interfaces_data = response.json()
            valid_data, _ = Functions.validate_pydantic_data(interfaces_data, schema=Interface)
            return valid_data
        except ValueError as e:
            raise ValueError(f"Invalid interface data received from API: {str(e)}")

    def get_by_id(self, interface_id: int) -> Dict[str, Any]:
        """Get a specific interface by its ID.
        
        Args:
            interface_id (int): The ID of the interface to retrieve
            
        Returns:
            Dict[str, Any]: Interface details including:
                - name (str): Interface name
                - type (str): Interface type (e.g., 'ADVANCED')
                - apps (Dict): Application configuration with:
                    - source (str): Source application name
                    - target (str): Target application name
            
        Raises:
            ValueError: If interface_id is not a positive integer or if the response data is invalid
            requests.exceptions.RequestException: If the API request fails
        """
        # Basic validation
        if not isinstance(interface_id, int) or interface_id <= 0:
            raise ValueError("interface_id must be a positive integer")

        response = self._brynq.session.get(
            f"{self._brynq.url}interfaces/{interface_id}"
        )
        response.raise_for_status()
        
        try:
            interface_data = response.json()
            valid_data, _ = Functions.validate_pydantic_data(interface_data, schema=InterfaceDetail)
            return valid_data[0]
        except ValueError as e:
            raise ValueError(f"Invalid interface data received from API: {str(e)}")

    def get_config(self, interface_id: int) -> Dict[str, Any]:
        """Get the base configuration of an interface.
        
        Args:
            interface_id (int): The ID of the interface
            
        Returns:
            Dict[str, Any]: Interface configuration including:
                - mapping (List): List of mapping configurations
                - variables (Dict): Configuration variables
            
        Raises:
            ValueError: If interface_id is not a positive integer or if the response data is invalid
            requests.exceptions.RequestException: If the API request fails
        """
        # Basic validation
        if not isinstance(interface_id, int) or interface_id <= 0:
            raise ValueError("interface_id must be a positive integer")

        response = self._brynq.session.get(
            f"{self._brynq.url}interfaces/{interface_id}/config"
        )
        response.raise_for_status()
        
        try:
            config_data = response.json()
            valid_data, _ = Functions.validate_pydantic_data(config_data, schema=InterfaceConfig)
            return valid_data[0]
        except ValueError as e:
            raise ValueError(f"Invalid interface configuration data: {str(e)}")

    def flush_config(self, interface_id: int) -> Dict[str, Any]:
        """
        Flushes the interface config to revert to a fresh state.
        
        Args:
            interface_id: The ID of the interface
            
        Returns:
            Dict[str, Any]: Response from the flush operation
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._brynq.session.get(
            url=f'{self._brynq.url}interfaces/{interface_id}/config/flush'
        )
        response.raise_for_status()
        return response

    def get_dataflows(self, interface_id: int) -> Dict[str, Any]:
        """
        Get the dataflows configuration of an interface.
        
        Args:
            interface_id: The ID of the interface
            
        Returns:
            Dict[str, Any]: Dataflows configuration
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._brynq.session.get(
            url=f'{self._brynq.url}interfaces/{interface_id}/config/dataflows'
        )
        response.raise_for_status()
        return response.json()

    def get_schedule(self, interface_id: int) -> Dict[str, Any]:
        """Get the schedule configuration of an interface.
        
        Args:
            interface_id (int): The ID of the interface
            
        Returns:
            Dict[str, Any]: Schedule configuration including:
                - id (int): The schedule ID
                - triggerType (str): Type of trigger (e.g., 'MANUAL')
                - triggerPattern (str): Pattern for the trigger
                - timezone (str): Timezone setting
                - nextReload (str, optional): Next scheduled reload time
                - frequency (Dict): Object containing day, hour, month, minute
                - startAfterPrecedingTask (bool, optional): Whether to start after preceding task
                - lastReload (str): Last reload time
                - lastErrorMessage (str): Last error message
            
        Raises:
            ValueError: If interface_id is not a positive integer or if the response data is invalid
            requests.exceptions.RequestException: If the API request fails
        """
        # Basic validation
        if not isinstance(interface_id, int) or interface_id <= 0:
            raise ValueError("interface_id must be a positive integer")

        response = self._brynq.session.get(
            f"{self._brynq.url}interfaces/{interface_id}/config/schedule"
        )
        response.raise_for_status()
        
        try:
            schedule_data = response.json()
            valid_data, _ = Functions.validate_pydantic_data(schedule_data, schema=Schedule)
            return valid_data[0]
        except ValueError as e:
            raise ValueError(f"Invalid schedule configuration data: {str(e)}")

    def get_template_config(self, interface_id: int) -> Dict[str, Any]:
        """
        Get the template configuration of an interface.
        
        Args:
            interface_id: The ID of the interface
            
        Returns:
            Dict[str, Any]: Template configuration
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = self._brynq.session.get(
            url=f'{self._brynq.url}interfaces/{interface_id}/template-config'
        )
        response.raise_for_status()
        return response.json()

    def get_scope(self, interface_id: int) -> Dict[str, Any]:
        """Get live and draft scopes from interface by id.
        
        Args:
            interface_id (int): The ID of the interface
            
        Returns:
            Dict[str, Any]: Scope configuration including:
                - live (Dict, optional): Live scope configuration
                - draft (Dict, optional): Draft scope configuration
            
        Raises:
            ValueError: If interface_id is not a positive integer or if the response data is invalid
            requests.exceptions.RequestException: If the API request fails
        """
        # Basic validation
        if not isinstance(interface_id, int) or interface_id <= 0:
            raise ValueError("interface_id must be a positive integer")

        response = self._brynq.session.get(
            f"{self._brynq.url}interfaces/{interface_id}/scope"
        )
        response.raise_for_status()
        
        try:
            scope_data = response.json()
            valid_data, _ = Functions.validate_pydantic_data(scope_data, schema=Scope)
            return valid_data[0]
        except ValueError as e:
            raise ValueError(f"Invalid scope data: {str(e)}")

    def get_dev_settings(self, interface_id: int) -> List[dict[str,Any]]:
        """Get the dev-settings of an interface

        Args:
            interface_id: Numeric ID of the interface

        Returns:
            Dict[str, Any]: A dictionary containing the dev settings:
                - dockerImage (str): Docker image name
                - sftpMapping (List[dict]): SFTP mapping configuration
                - runfilePath (str): Path to the runfile
                - stopIsAllowed (bool): Whether stopping is allowed

        Raises:
            requests.exceptions.RequestException: If the API request fails
            requests.exceptions.HTTPError: If dev settings not found (404)
            ValueError: If interface_id is not a positive integer
        """
        if not isinstance(interface_id, int) or interface_id <= 0:
            raise ValueError("interface_id must be a positive integer")

        response = self._brynq.session.get(
            url=f"{self._brynq.url}interfaces/{interface_id}/config/dev-settings"
        )
        response.raise_for_status()
        
        valid_data, _ = Functions.validate_pydantic_data(response.json(), schema=DevSettings)
        return valid_data
