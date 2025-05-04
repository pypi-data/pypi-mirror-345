from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseFormatter(ABC):
    """
    Base abstract class for all text formatters.
    """
    
    def __init__(self):
        """
        Initialize the formatter.
        """
        pass
    
    @abstractmethod
    def format(self, text: str, **kwargs) -> str:
        """
        Format the input text according to the formatter's rules.
        
        Args:
            text: Input text to format.
            **kwargs: Additional formatting options.
            
        Returns:
            Formatted text.
        """
        pass 