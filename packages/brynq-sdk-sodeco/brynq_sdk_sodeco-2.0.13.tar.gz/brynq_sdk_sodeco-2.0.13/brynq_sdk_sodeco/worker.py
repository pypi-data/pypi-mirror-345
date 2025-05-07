from datetime import datetime
import pandas as pd
import warnings
from .costcentres import CostCentres
from .dimona import Dimonas
from .replacement import Replacements
from .car import Cars
from .schemas.worker import GetWorkerSchema, PostWorkerSchema
from .schemas import DATEFORMAT
from .absences import Absences
from .absencenote import AbsenceNotes
from .communication import Communications
from .contract import Contracts
from .family import Families
from .tax import Taxes
from .salarycomposition import SalaryCompositions
from .base import SodecoBase
from typing import Optional, Dict, Any
from .divergentsalary import DivergentSalaryScale
from .divergentpayment import DivergentPayments
from .leavecounters import LeaveCounters
from .address import Addresses
from .schedule import Schedules
from brynq_sdk_functions import Functions


class Workers(SodecoBase):
    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}worker"
        self.addresses = Addresses(sodeco)
        self.communications = Communications(sodeco)
        self.contracts = Contracts(sodeco)
        self.costcentres = CostCentres(sodeco)
        self.families = Families(sodeco)
        self.taxes = Taxes(sodeco)
        self.replacements = Replacements(sodeco)
        self.absences = Absences(sodeco)
        self.absencenotes = AbsenceNotes(sodeco)
        self.cars = Cars(sodeco)
        self.dimonas = Dimonas(sodeco)
        self.divergentsalaries = DivergentSalaryScale(sodeco)
        self.divergentpayments = DivergentPayments(sodeco)
        self.leavecounters = LeaveCounters(sodeco)
        self.salarycompositions = SalaryCompositions(sodeco)
        self.schedules = Schedules(sodeco)

    def get(self, worker_id: Optional[str] = None, start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Get worker information, optionally filtered by worker_id and date range.
        
        Args:
            worker_id: Optional worker ID to get specific worker
            start_date: Start date for filtering workers
            end_date: End date for filtering workers (required if start_date is provided)
            
        Returns:
            pd.DataFrame: DataFrame containing worker information
            
        Raises:
            ValueError: If start_date is provided without end_date
        """
        url = self.url
        if worker_id is not None:
            url += f"/{worker_id}"
        if start_date is not None:
            if end_date is not None:
                url += f"/{start_date.strftime(DATEFORMAT)}/{end_date.strftime(DATEFORMAT)}"
            else:
                raise ValueError("if start_date is specified, end_date must be specified as well")

        limit = 100
        offset = 0
        all_data = []
        
        while True:
            batch_data = self._make_request_with_polling(url, params={"limit": limit, "offset": offset})
            all_data.extend(batch_data)
            
            # If we got fewer results than the limit, we've reached the end
            if len(batch_data) < limit:
                break
                
            # Increment offset for next batch
            offset += limit

        employee = pd.DataFrame(all_data)
        employee = employee.drop(columns=['FamilyStatus', 'address', 'Communication', 'contract', 'Tax', 'Replacement'])
        employee = self._rename_camel_columns_to_snake_case(employee)
        addresses = pd.json_normalize(all_data,
                                      record_path='address',
                                      meta=['WorkerNumber']
                                      )
        addresses = self._rename_camel_columns_to_snake_case(addresses)
        family = pd.json_normalize(all_data,
                                   record_path='FamilyStatus',
                                   meta=['WorkerNumber']
                                   )
        family = self._rename_camel_columns_to_snake_case(family)
        communication = pd.json_normalize(all_data,
                                          record_path='Communication',
                                          meta=['WorkerNumber']
                                          )
        communication = self._rename_camel_columns_to_snake_case(communication)
        contract = pd.json_normalize(all_data,
                                     record_path='contract',
                                     meta=['WorkerNumber']
                                     )
        salary_compositions = pd.json_normalize(all_data,
                                     record_path=['contract', 'SalaryCompositions'],
                                     meta=['WorkerNumber']
                                     )
        salary_compositions = self._rename_camel_columns_to_snake_case(salary_compositions)
        contract = self._rename_camel_columns_to_snake_case(contract)
        contract = contract.drop(columns=['salary_compositions'])
        tax = pd.json_normalize(all_data,
                                record_path='Tax',
                                meta=['WorkerNumber']
                                )
        tax = self._rename_camel_columns_to_snake_case(tax)
        replacement = pd.json_normalize(all_data,
                                        record_path='Replacement',
                                        meta=['WorkerNumber']
                                        )
        replacement = self._rename_camel_columns_to_snake_case(replacement)

        return employee, family, addresses, communication, contract, tax, replacement, salary_compositions

    def create(self, payload: Dict[str, Any], debug: bool = False) -> dict:
        """
        Create a worker based on the given payload.
        The payload must adhere to the structure defined by the PostWorkerSchema.
        
        Args:
            payload: The worker data to create
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created worker data
            
        Raises:
            ValueError: If the payload is invalid
        """
        try:
            # Validate the payload using PostWorkerSchema
            validated_data = PostWorkerSchema(**payload).dict()
            
            # Send the POST request to create the worker
            headers, data = self._prepare_raw_request(validated_data)
            resp_data = self._make_request_with_polling(
                self.url,
                method='POST',
                headers=headers,
                data=data
            )
            return resp_data
        except Exception as e:
            error_msg = "Invalid worker payload"
            if debug:
                error_msg += f": {str(e)}"
            raise ValueError(error_msg)

    def update(self, worker_id: str, payload: Dict[str, Any], debug: bool = False) -> dict:
        """
        Update a worker's information.
        The payload must adhere to the structure defined by the PostWorkerSchema.
        
        Args:
            worker_id: The ID of the worker to update
            payload: The worker data to update
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The updated worker data
            
        Raises:
            ValueError: If the payload is invalid
        """
        url = f"{self.url}/{worker_id}"
        
        df = pd.DataFrame([payload])
        valid_data, invalid_data = Functions.validate_data(df, GetWorkerSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid worker payload"
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

    def get_new_worker_number(self):
        url = f"{self.sodeco.base_url}newworkernumber"
        resp = self._make_request_with_polling(url)
        return resp