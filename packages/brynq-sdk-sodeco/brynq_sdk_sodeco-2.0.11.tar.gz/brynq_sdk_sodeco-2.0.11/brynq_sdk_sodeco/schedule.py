import pandas as pd
from .base import SodecoBase
from .schemas.schedule import ScheduleSchema, ScheduleWeekSchema
from brynq_sdk_functions import Functions
from typing import Optional, List, Dict, Any


class Schedules(SodecoBase):
    """Class for managing worker schedules in Sodeco."""

    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}schedule"

    def get(self) -> pd.DataFrame:
        """
        Get schedule information for a worker.
        
        Args:
            worker_id: The worker ID to get schedule information for
            
        Returns:
            pd.DataFrame: DataFrame containing the schedule information
        """
        data = self._make_request_with_polling(self.url)
        return pd.DataFrame(data)

    def create(self, payload: Dict[str, Any], debug: bool = False) -> dict:
        """
        Create a schedule entry for a worker.
        The payload must adhere to the structure defined by the ScheduleSchema.
        
        Args:
            worker_id: The ID of the worker to create a schedule entry for
            payload: The schedule data to create. Must include ScheduleID, Description,
                    StartDate, and Week (list of week schedules)
            debug: If True, prints detailed validation errors
            
        Returns:
            dict: The created schedule data
            
        Raises:
            ValueError: If the payload is invalid or Week data doesn't match schema
        """
        # First validate the main schedule data
        schedule_data = {
            'ScheduleID': payload.get('ScheduleID'),
            'Description': payload.get('Description'),
            'StartDate': payload.get('StartDate'),
            'Week': payload.get('Week')
        }
        df = pd.DataFrame([schedule_data])
        valid_data, invalid_data = Functions.validate_data(df, ScheduleSchema, debug=debug)

        if len(invalid_data) > 0:
            error_msg = "Invalid schedule payload"
            if debug:
                error_msg += f": {invalid_data.to_dict(orient='records')}"
            raise ValueError(error_msg)

        # Then validate the week data
        weeks = payload.get('Week', [])
        if not ScheduleSchema.validate_weeks(weeks):
            error_msg = "Invalid schedule week data"
            if debug:
                error_msg += f": {weeks}"
            raise ValueError(error_msg)

        # Combine the validated data
        final_payload = valid_data.iloc[0].to_dict()
        final_payload['Week'] = weeks

        # Send the POST request to create the schedule entry
        headers, data = self._prepare_raw_request(final_payload)
        data = self._make_request_with_polling(
            self.url,
            method='POST',
            headers=headers,
            data=data
        )
        return data
