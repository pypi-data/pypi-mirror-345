from typing import Optional
import pandas as pd
from datetime import datetime
from .schemas import DATEFORMAT
from .base import SodecoBase
from .schemas.salarycomposition import SalaryCompositionSchema
from brynq_sdk_functions import Functions


class SalaryCompositions(SodecoBase):
    """Class for managing salary compositions in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """
        Create a salary composition entry for a worker.
        The payload must adhere to the structure defined by the SalaryCompositionSchema.
        
        Args:
            worker_id: The ID of the worker to create a salary composition entry for
            payload: The salary composition data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created salary composition data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/salarycomposition"
        
        # Convert payload to DataFrame and validate
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, SalaryCompositionSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid salary composition payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the POST request to create the salary composition entry
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='POST',
            headers=headers,
            data=data
        )
        return data

    def update(self, worker_id: str, salary_code: str, start_date: datetime, payload: dict, debug: bool = False) -> dict:
        """
        Update a salary composition entry for a worker.
        The payload must adhere to the structure defined by the SalaryCompositionSchema.
        
        Args:
            worker_id: The ID of the worker who owns the salary composition
            salary_code: The salary code to update
            start_date: The start date of the salary composition
            payload: The salary composition data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated salary composition data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}/salarycomposition/{salary_code}/{start_date.strftime(DATEFORMAT)}"
        
        # Validate the payload
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, SalaryCompositionSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid salary composition payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Send the PUT request to update the salary composition
        headers, data = self._prepare_raw_request(valid_data.iloc[0].to_dict())
        data = self._make_request_with_polling(
            url,
            method='PUT',
            headers=headers,
            data=data
        )
        return data

    def delete(self, worker_id: str, salary_code: str, start_date: datetime) -> dict:
        """
        Delete a salary composition entry for a worker.
        
        Args:
            worker_id: The ID of the worker who owns the salary composition
            salary_code: The salary code to delete
            start_date: The start date of the salary composition to delete
            
        Returns:
            dict: The response from the server
        """
        url = f"{self.url}/{worker_id}/salarycomposition/{salary_code}/{start_date.strftime(DATEFORMAT)}"
        
        # Send the DELETE request
        data = self._make_request_with_polling(
            url,
            method='DELETE'
        )
        return data
