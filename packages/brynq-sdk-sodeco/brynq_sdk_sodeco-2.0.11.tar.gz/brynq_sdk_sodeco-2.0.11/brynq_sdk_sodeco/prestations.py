from typing import Dict, Any, Optional
import pandas as pd
from .base import SodecoBase
from .schemas.prestation import PrestationModel
import json

class Prestations(SodecoBase):
    """Class for managing prestations in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}prestations"

    def create(self, payload: Dict[str, Any], debug: bool = False) -> dict:
        """
        Create a prestation entry.
        The payload must adhere to the structure defined by the PrestationModel.
        
        Args:
            payload: The prestation data to create
            debug: If True, only validate the payload without making the request
        
        Returns:
            dict: Response from the API
            
        Raises:
            ValueError: If the payload is invalid
        """
        # Validate the main prestation data using Pydantic
        try:
            validated_data = PrestationModel(**payload)
        except Exception as e:
            raise ValueError(f"Invalid prestation data: {str(e)}")
            
        # If debug mode, return without making request
        if debug:
            return {"status": "valid"}
            
        # Send the POST request to create the prestation entry
        filtered_data = self._filter_nan_values(validated_data.dict())
        data = self._make_request_with_polling(
            self.url,
            method='POST',
            data=json.dumps([filtered_data])  # Manually encode as JSON string
        )
        return data

    def delete(self, payload: Dict[str, Any]) -> dict:
        """
        Delete prestations for a worker in a specific month and year.
        
        Args:
            payload: Dictionary containing:
                    - WorkerNumber: The worker number to delete prestations for
                    - Month: The month to delete prestations for (1-12)
                    - Year: The year to delete prestations for
        
        Returns:
            dict: Response from the API
            
        Raises:
            ValueError: If the payload is invalid
        """
        # Validate the payload
        if not PrestationModel.validate_delete(payload):
            raise ValueError("Invalid delete prestation data")
            
        url = f"{self.url}/{payload['WorkerNumber']}/{payload['Year']}/{payload['Month']:02d}"
        return self._make_request_with_polling(url, method='DELETE')

    def complete(self, payload: Dict[str, Any]) -> dict:
        """
        Mark prestations as completed for processing in the system.
        
        Args:
            payload: Dictionary containing:
                    - Month: The month to mark as completed (1-12)
                    - Year: The year to mark as completed
                    - Correction: Optional flag to indicate if this is a correction ('Y' or 'N')
        
        Returns:
            dict: Response from the API
            
        Raises:
            ValueError: If the payload is invalid
        """
        # Validate the payload
        if not PrestationModel.validate_completed(payload):
            raise ValueError("Invalid completed prestation data")
            
        # Send the POST request to mark prestations as completed
        filtered_data = self._filter_nan_values(payload)
        data = self._make_request_with_polling(
            f"{self.url}/completed",
            method='POST',
            headers={"Content-Type": "application/json"},
            data=json.dumps([filtered_data])  # Manually encode as JSON string
        )
        return data
