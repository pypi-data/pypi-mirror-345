from typing import Optional
from datetime import datetime
import pandas as pd

from .base import SodecoBase
from .schemas.contract import ContractModel
from .schemas import DATEFORMAT
from brynq_sdk_functions import Functions
from typing import Dict, Any, Optional
from datetime import datetime
from .base import SodecoBase
from .schemas.contract import ContractModel
from .schemas import DATEFORMAT
import json

class Contracts(SodecoBase):
    """Contract of a Worker"""
    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"

    def create(self, worker_id: str, payload: dict, debug: bool = False) -> dict:
        """Create a contract for a worker.
        
        Args:
            worker_id: Worker ID
            payload: Contract data
            debug: Print debug info
            
        Returns:
            dict: Response from the API
            
        Raises:
            ValueError: If the payload doesn't validate against the ContractModel schema
        """
        try:
            # Validate payload using Pydantic model
            validated_data = ContractModel(**payload)
        except Exception as e:
            raise ValueError(f"Invalid contract data: {str(e)}")
            
        # If debug mode, return without making request
        if debug:
            return validated_data.dict()
            
        # Send the POST request to create the contract
        headers, data = self._prepare_raw_request(validated_data.dict())
        response = self._make_request_with_polling(
            url=f"{self.url}/{worker_id}/contract",
            method="POST",
            headers=headers,
            data=data
        )
        return response

    def update(self, worker_id: str, contract_date: datetime, payload: dict, debug: bool = False) -> dict:
        """Update a contract for a worker.
        
        Args:
            worker_id: Worker ID
            contract_date: Contract start date
            payload: Contract data
            debug: Print debug info
            
        Returns:
            dict: Response from the API
            
        Raises:
            ValueError: If the payload doesn't validate against the ContractModel schema
        """
        try:
            # Validate payload using Pydantic model
            validated_data = ContractModel(**payload)
        except Exception as e:
            raise ValueError(f"Invalid contract data: {str(e)}")
            
        # If debug mode, return without making request
        if debug:
            return validated_data.dict()
            
        # Send the PUT request to update the contract
        headers, data = self._prepare_raw_request(validated_data.dict())
        response = self._make_request_with_polling(
            url=f"{self.url}/{worker_id}/contract/{contract_date.strftime(DATEFORMAT)}",
            method="PUT",
            headers=headers,
            data=data
        )
        return response

    def get(self, worker_id: str, ref_date: Optional[datetime] = None) -> dict:
        """Get contracts for a worker.
        
        Args:
            worker_id: Worker ID
            ref_date: Optional reference date
            
        Returns:
            dict: Response from the API
        """
        url = f"{self.url}/{worker_id}/contract"
        if ref_date is not None:
            url += f"/{ref_date.strftime(DATEFORMAT)}"
        
        data = self._make_request_with_polling(url)
        return data

    def delete(self, worker_id: str, contract_date: datetime, debug: bool = False) -> dict:
        """Delete a contract for a worker.
        
        Args:
            worker_id: Worker ID
            contract_date: Contract start date
            debug: Print debug info
            
        Returns:
            dict: Response from the API
        """
        data = self._make_request_with_polling(
            url=f"{self.url}/{worker_id}/contract/{contract_date.strftime(DATEFORMAT)}",
            method="DELETE"
        )
        return data
