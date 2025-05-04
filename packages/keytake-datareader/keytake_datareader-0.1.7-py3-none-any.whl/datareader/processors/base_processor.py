from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseProcessor(ABC):
    """
    Base abstract class for all data processors.
    """
    
    def __init__(self):
        """
        Initialize the processor.
        """
        pass
    
    @abstractmethod
    def process(self, source: str, **kwargs) -> str:
        """
        Process the input source and return extracted text.
        
        Args:
            source: Path to file or URL to process.
            **kwargs: Additional processing options.
            
        Returns:
            Extracted text in plain format.
        """
        pass
    
    def preprocess(self, text: str, **kwargs) -> str:
        """
        Preprocess the extracted text (clean up, normalize, etc.).
        
        Args:
            text: Raw extracted text.
            **kwargs: Additional preprocessing options.
            
        Returns:
            Preprocessed text.
        """
        # Default implementation simply returns the input
        return text
    
    def extract_metadata(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from the source.
        
        Args:
            source: Path to file or URL.
            **kwargs: Additional options.
            
        Returns:
            Dictionary of metadata.
        """
        # Default implementation returns empty metadata
        return {} 