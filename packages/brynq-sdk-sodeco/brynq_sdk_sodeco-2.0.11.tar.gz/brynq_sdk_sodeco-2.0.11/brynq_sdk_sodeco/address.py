from typing import Optional
import pandas as pd
from datetime import datetime
import json

from .base import SodecoBase
from .schemas.address import AddressSchema
from .schemas import DATEFORMAT
from brynq_sdk_functions import Functions


class Addresses(SodecoBase):
    """Class for managing addresses in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: str) -> pd.DataFrame:
        """
        Get address information for a worker.
        
        Args:
            worker_id: The worker ID to get address for
            
        Returns:
            pd.DataFrame: DataFrame containing the address information
        """
        url = f"{self.url}/{worker_id}/address"
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create an address for a worker.
        The payload must adhere to the structure defined by the AddressSchema.
        
        Args:
            worker_id: The ID of the worker to create an address for
            payload: The address data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created address data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/address"
        
        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, AddressSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid address payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the address
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, address_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update an address for a worker.
        The payload must adhere to the structure defined by the AddressSchema.
        
        Args:
            worker_id: The ID of the worker who owns the address
            address_date: The start date of the address to update
            payload: The address data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated address data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/address/{address_date.strftime(DATEFORMAT)}"
        
        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, AddressSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid address payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the address
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, address_date: datetime) -> dict:
        """
        Delete an address entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the address
            address_date: The start date of the address to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/address/{address_date.strftime(DATEFORMAT)}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
