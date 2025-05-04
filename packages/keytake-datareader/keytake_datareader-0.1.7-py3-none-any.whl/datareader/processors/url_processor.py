from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

from datareader.processors.base_processor import BaseProcessor

class URLProcessor(BaseProcessor):
    """
    Processor for extracting text from web pages.
    """
    
    def process(self, source: str, **kwargs) -> str:
        """
        Process a URL and extract its text content.
        
        Args:
            source: URL to scrape.
            headers: Optional custom headers for the request.
            timeout: Request timeout in seconds.
            content_tags: HTML tags to extract content from (default: p, h1-h6, li, div).
            **kwargs: Additional processing options.
            
        Returns:
            Extracted text from the web page.
        """
        # Get processing options
        headers = kwargs.get('headers', {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        timeout = kwargs.get('timeout', 10)
        content_tags = kwargs.get('content_tags', ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div'])
        
        # Make the request
        response = requests.get(source, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract text based on content tags
        extracted_text = ""
        for tag_name in content_tags:
            for tag in soup.find_all(tag_name):
                if tag.text.strip():
                    # Add title formatting for headings
                    if tag_name.startswith('h') and len(tag_name) == 2:
                        level = int(tag_name[1])
                        prefix = '#' * level + ' '
                        extracted_text += prefix + tag.text.strip() + "\n\n"
                    else:
                        extracted_text += tag.text.strip() + "\n\n"
        
        # Preprocess the extracted text
        return self.preprocess(extracted_text, **kwargs)
    
    def preprocess(self, text: str, **kwargs) -> str:
        """
        Preprocess the extracted web text.
        
        Args:
            text: Raw extracted text from webpage.
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
        Extract metadata from a web page.
        
        Args:
            source: URL to scrape.
            **kwargs: Additional options.
            
        Returns:
            Dictionary of webpage metadata.
        """
        metadata = {
            'url': source
        }
        
        # Get request options
        headers = kwargs.get('headers', {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        timeout = kwargs.get('timeout', 10)
        
        # Make the request
        response = requests.get(source, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract page title
        if soup.title:
            metadata['title'] = soup.title.string
            
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
                
        return metadata 