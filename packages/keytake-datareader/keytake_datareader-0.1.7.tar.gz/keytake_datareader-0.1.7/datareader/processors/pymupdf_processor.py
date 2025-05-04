import os
from typing import Dict, Any, Optional, List

import pymupdf

from datareader.processors.base_processor import BaseProcessor

class PyMuPDFProcessor(BaseProcessor):
    """
    Processor for extracting text from PDF files using PyMuPDF (fitz).
    
    Generally faster and with more features than PyPDF2, but with a different license.
    """
    
    def process(self, source: str, **kwargs) -> str:
        """
        Process a PDF file and extract its text content using PyMuPDF.
        
        Args:
            source: Path to the PDF file.
            pages: Optional list of page numbers to extract (1-indexed).
            images: Whether to extract images (not implemented yet).
            **kwargs: Additional processing options.
            
        Returns:
            Extracted text from the PDF.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"PDF file not found: {source}")
        
        pages = kwargs.get('pages', None)
        extract_images = kwargs.get('images', False)
        
        extracted_text = ""
        
        try:
            # Open the PDF file
            doc = pymupdf.open(source)
            total_pages = len(doc)
            
            # Define which pages to process
            if pages is None:
                page_indices = range(total_pages)
            else:
                # Convert 1-indexed page numbers to 0-indexed
                page_indices = [p-1 for p in pages if 1 <= p <= total_pages]
            
            # Extract text from each page
            for i in page_indices:
                page = doc[i]
                page_text = page.get_text()
                if page_text:
                    extracted_text += page_text + "\n\n"
            
            # TODO: Implement image extraction if requested
            if extract_images:
                pass  # Future enhancement
                
            # Close the document
            doc.close()
            
        except Exception as e:
            raise RuntimeError(f"Error processing PDF with PyMuPDF: {str(e)}")
        
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
            # Replace multiple spaces with a single space, preserving newlines
            lines = text.split('\n')
            processed_lines = [' '.join(line.split()) for line in lines]
            text = '\n'.join(processed_lines)
            
        if remove_empty_lines:
            lines = text.split('\n')
            text = '\n'.join([line for line in lines if line.strip()])
        
        return text
    
    def extract_metadata(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file using PyMuPDF.
        
        Args:
            source: Path to the PDF file.
            **kwargs: Additional options.
            
        Returns:
            Dictionary of PDF metadata.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"PDF file not found: {source}")
        
        metadata = {}
        
        try:
            # Open the PDF
            doc = pymupdf.open(source)
            
            # Get basic document info
            metadata['PageCount'] = len(doc)
            metadata['Title'] = doc.metadata.get('title', '')
            metadata['Author'] = doc.metadata.get('author', '')
            metadata['Subject'] = doc.metadata.get('subject', '')
            metadata['Keywords'] = doc.metadata.get('keywords', '')
            metadata['Creator'] = doc.metadata.get('creator', '')
            metadata['Producer'] = doc.metadata.get('producer', '')
            
            # Add file size
            metadata['FileSize'] = os.path.getsize(source)
            
            # Extract PDF version
            metadata['PDFVersion'] = f"{doc.version}"
            
            # Close the document
            doc.close()
            
        except Exception as e:
            # Return partial metadata if there was an error
            metadata['Error'] = str(e)
            
        return metadata 