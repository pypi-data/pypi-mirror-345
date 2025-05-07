from typing import Optional, Dict, Any
from datetime import datetime
import base64
import os

from .base import SodecoBase
from .schemas.document import DocumentModel, DocumentTypeEnum, LanguageEnum

# Date format YYYYMMDD
DATEFORMAT = "%Y%m%d"


class Documents(SodecoBase):
    """Document management in Sodeco Prisma"""
    
    def __init__(self, sodeco):
        super().__init__(sodeco)
        self.url = f"{self.sodeco.base_url}document"
    
    def create(self, payload: dict, debug: bool = False) -> dict:
        """Create a document in Prisma.
        
        Args:
            payload: Complete document data dictionary
            debug: If True, only validate without sending request
            
        Returns:
            dict: Response from the API containing the document ID
            
        Raises:
            ValueError: If the document data is invalid
        """
        # Validate document data
        try:
            # Validate payload using Pydantic model
            validated_data = DocumentModel(**payload)
        except Exception as e:
            raise ValueError(f"Invalid document data: {str(e)}")
            
        # If debug mode, return without making request
        if debug:
            return validated_data.dict()
        
        # Send the POST request to upload the document
        headers, data = self._prepare_raw_request(validated_data.dict())
        response = self._make_request_with_polling(
            url=self.url,
            method="POST",
            headers=headers,
            data=data
        )
        return response
    
    def list(self, start_date: datetime, end_date: datetime) -> dict:
        """Get a list of available documents within the given period.
        
        The list includes both documents for the employer and documents 
        for the employees of that employer. Each document has a unique ID
        that can be used to retrieve the document itself.
        
        Args:
            start_date: The start date of the period
            end_date: The end date of the period
            
        Returns:
            dict: List of available documents
        """
        url = f"{self.url}/listing/{start_date.strftime(DATEFORMAT)}/{end_date.strftime(DATEFORMAT)}"
        data = self._make_request_with_polling(url)
        return data
    
    def get_withdrawn_documents(self, start_date: datetime) -> dict:
        """Get a list of withdrawn documents from the given start date.
        
        Withdrawn documents are documents that the social secretariat has
        recalled for some reason. This request is NOT per employer,
        the response contains the employer number along with the document ID.
        
        Args:
            start_date: The start date from which to get withdrawn documents
            
        Returns:
            dict: List of withdrawn documents
        """
        url = f"{self.url}/listing/withdrawals/{start_date.strftime(DATEFORMAT)}"
        data = self._make_request_with_polling(url)
        return data
    
    def get(self, document_id: str, output_path: Optional[str] = None) -> dict:
        """Get a specific document by its ID.
        
        The document ID can be obtained via the list method.
        The result consists of a base64 converted byte array.
        
        If output_path is provided, the document will be saved to that location
        and the path to the saved file will be added to the returned document data.
        
        Args:
            document_id: The ID of the document to retrieve
            output_path: Optional path where to save the document
            
        Returns:
            dict: The document data, with an additional 'saved_path' key if output_path was provided
            
        Raises:
            ValueError: If the output_path is provided but the document cannot be saved
        """
        # Get the document from the API
        url = f"{self.url}/{document_id}"
        document_data = self._make_request_with_polling(url)
        
        # If output_path is not provided, just return the document data
        if output_path is None:
            return document_data
        
        # Save the document to the specified path
        try:
            # Extract base64 content and filename
            if "Document" not in document_data:
                raise ValueError("Invalid document data: Missing 'Document' field")
            
            if "Filename" not in document_data:
                # Use a default filename if none is provided
                filename = "document"
            else:
                filename = document_data["Filename"]
            
            # Create full output path
            if os.path.isdir(output_path):
                # If output_path is a directory, append the filename
                full_path = os.path.join(output_path, filename)
            else:
                # Otherwise use the provided path as is
                full_path = output_path
            
            # Decode base64 content
            try:
                content = base64.b64decode(document_data["Document"])
            except Exception as e:
                raise ValueError(f"Failed to decode document content: {str(e)}")
            
            # Save to file
            with open(full_path, "wb") as file:
                file.write(content)
            
            # Add the saved path to the document data
            document_data["saved_path"] = full_path
            
            return document_data
            
        except Exception as e:
            # If there's an error during saving, add an error message to the document data
            document_data["save_error"] = str(e)
            return document_data
