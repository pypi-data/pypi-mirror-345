import os
from typing import Dict, Any, Optional, List

import pypdf

from datareader.processors.base_processor import BaseProcessor

class PDFProcessor(BaseProcessor):
    """
    Processor for extracting text from PDF files.
    """
    
    def process(self, source: str, **kwargs) -> str:
        """
        Process a PDF file and extract its text content.
        
        Args:
            source: Path to the PDF file.
            pages: Optional list of page numbers to extract (1-indexed).
            **kwargs: Additional processing options.
            
        Returns:
            Extracted text from the PDF.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"PDF file not found: {source}")
        
        pages = kwargs.get('pages', None)
        
        extracted_text = ""
        
        with open(source, 'rb') as file:
            reader = pypdf.PdfReader(file)
            total_pages = len(reader.pages)
            
            # Define which pages to process
            if pages is None:
                page_indices = range(total_pages)
            else:
                # Convert 1-indexed page numbers to 0-indexed
                page_indices = [p-1 for p in pages if 1 <= p <= total_pages]
            
            # Extract text from each page
            for i in page_indices:
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n\n"
        
        # Preprocess the extracted text
        return self.preprocess(extracted_text, **kwargs)
    
    def preprocess(self, text: str, **kwargs) -> str:
        """
        Preprocess the extracted PDF text.
        
        Args:
            text: Raw extracted text from PDF.
            remove_empty_lines: Whether to remove empty lines.
            normalize_whitespace: Whether to normalize whitespace.
            **kwargs: Additional preprocessing options.
            
        Returns:
            Preprocessed text.
        """
        # Get preprocessing options
        remove_empty_lines = kwargs.get('remove_empty_lines', True)
        normalize_whitespace = kwargs.get('normalize_whitespace', True)
        
        # Apply preprocessing
        if normalize_whitespace:
            text = ' '.join(text.split())
            
        if remove_empty_lines:
            lines = text.split('\n')
            text = '\n'.join([line for line in lines if line.strip()])
        
        return text
    
    def extract_metadata(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file.
        
        Args:
            source: Path to the PDF file.
            **kwargs: Additional options.
            
        Returns:
            Dictionary of PDF metadata.
        """
        metadata = {}
        
        if not os.path.exists(source):
            raise FileNotFoundError(f"PDF file not found: {source}")
        
        with open(source, 'rb') as file:
            reader = pypdf.PdfReader(file)
            
            # Extract document information
            if reader.metadata:
                for key, value in reader.metadata.items():
                    if key.startswith('/'):
                        clean_key = key[1:]
                    else:
                        clean_key = key
                    metadata[clean_key] = value
            
            # Add page count
            metadata['PageCount'] = len(reader.pages)
            
        return metadata 