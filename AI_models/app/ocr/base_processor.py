from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BaseDocumentProcessor(ABC):
    """
    Abstract base class for document OCR & parsing processors.
    Future processors (VisaProcessor, NationalIDProcessor, DrivingLicenseProcessor)
    must implement these methods to ensure loose coupling.
    """

    @abstractmethod
    def process_document(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract structured fields from document image.
        Must return standard dictionary schema containing at minimum:
        {
            "document_type": str,
            "name": str,
            "document_number": str,
            "nationality": str,
            "dob": str,
            "gender": str,
            "expiry": str,
            "confidence": float,
            "raw_text": Optional[str]
        }
        """
        pass

    @abstractmethod
    def get_supported_document_type(self) -> str:
        """Returns string identifier of supported document type (e.g. 'passport', 'visa')."""
        pass
