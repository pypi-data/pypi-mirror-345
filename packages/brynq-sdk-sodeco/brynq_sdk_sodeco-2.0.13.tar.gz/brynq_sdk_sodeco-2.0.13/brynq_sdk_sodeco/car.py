from typing import Optional
import pandas as pd
from datetime import datetime
from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas.car import CarSchema
from brynq_sdk_functions import Functions

class Cars(SodecoBase):
    """Class for managing company cars in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def get(self, worker_id: Optional[str] = None, start_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get company car information.
        
        Args:
            worker_id: Optional worker ID to get company car information for a specific worker
            start_date: Optional start date to get company car information for a specific date
            
        Returns:
            pd.DataFrame: DataFrame containing the company car information
        """
        if worker_id and start_date:
            url = f"{self.url}/{worker_id}/companycar/{start_date.strftime(DATEFORMAT)}"
        elif worker_id:
            url = f"{self.url}/{worker_id}/companycar"
        else:
            url = f"{self.sodeco.base_url}companycar"
        
        data = self._make_request_with_polling(url)
        return pd.DataFrame(data)

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create a company car entry for a worker.
        The payload must adhere to the structure defined by the CarSchema.
        
        Args:
            worker_id: The ID of the worker to create a company car entry for
            payload: The company car data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created company car data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/companycar"
        
        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, CarSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid company car payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the car
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, car_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update a car entry for a worker.
        The payload must adhere to the structure defined by the CarSchema.
        
        Args:
            worker_id: The ID of the worker who owns the car entry
            car_date: The start date of the car entry to update
            payload: The car data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated car data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/companycar/{car_date.strftime(DATEFORMAT)}"
        
        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, CarSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid car payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the car
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, car_date: datetime) -> dict:
        """
        Delete a car entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the car entry
            car_date: The start date of the car entry to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/companycar/{car_date.strftime(DATEFORMAT)}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
