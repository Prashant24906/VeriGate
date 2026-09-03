import numpy as np
from typing import Dict, Any, Type
from app.ocr.base_processor import BaseDocumentProcessor
from app.ocr.passport_processor import PassportProcessor


# Processor Registry mapping document types to processor classes
PROCESSOR_REGISTRY: Dict[str, Type[BaseDocumentProcessor]] = {
    "passport": PassportProcessor
}


def register_processor(doc_type: str, processor_cls: Type[BaseDocumentProcessor]):
    """Register a new document processor implementation (e.g. VisaProcessor)."""
    PROCESSOR_REGISTRY[doc_type.lower()] = processor_cls


def extract_document(image: np.ndarray, document_type: str = "passport") -> Dict[str, Any]:
    """
    Standard OCR entry point.
    Dispatches document image to the appropriate document processor.
    """
    doc_type_key = document_type.lower()
    
    if doc_type_key not in PROCESSOR_REGISTRY:
        # Fall back to passport processor if unknown
        doc_type_key = "passport"

    processor = PROCESSOR_REGISTRY[doc_type_key]()
    return processor.process_document(image)
