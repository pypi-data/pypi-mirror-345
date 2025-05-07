from typing import Optional
import pandas as pd
from datetime import datetime

from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas.family import FamilySchema
from brynq_sdk_functions import Functions


class Families(SodecoBase):
    """Class for managing family status in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str) -> pd.DataFrame:
        """
        Get family status information for a worker.
        
        Args:
            worker_id: The worker ID to get family status for
            
        Returns:
            pd.DataFrame: DataFrame containing the family status information
        """
        url = f"{self.url}/{worker_id}/familystatus"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create a family status entry for a worker.
        The payload must adhere to the structure defined by the FamilySchema.
        
        Args:
            worker_id: The ID of the worker to create a family status for
            payload: The family status data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created family status data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/familystatus"
        
        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, FamilySchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid family status payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the family status
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, family_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update a family member for a worker.
        The payload must adhere to the structure defined by the FamilySchema.
        
        Args:
            worker_id: The ID of the worker who owns the family member
            family_date: The start date of the family status to update
            payload: The family member data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated family member data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/familystatus/{family_date.strftime(DATEFORMAT)}"
        
        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, FamilySchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid family member payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the family member
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, family_date: datetime) -> dict:
        """
        Delete a family status entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the family status
            family_date: The start date of the family status to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/familystatus/{family_date.strftime(DATEFORMAT)}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
