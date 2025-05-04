from typing import Dict, Any, Optional
import re
try:
    import markitdown
except ImportError:
    markitdown = None

from datareader.processors.base_processor import BaseProcessor

class MarkitdownProcessor(BaseProcessor):
    """
    Processor for converting text to enhanced markdown format using the markitdown library.
    """
    
    def __init__(self):
        """Initialize the processor and check if markitdown is available."""
        super().__init__()
        self._has_markitdown = markitdown is not None
    
    def process(self, source: str, **kwargs) -> str:
        """
        Process text and convert it to enhanced markdown format.
        
        Args:
            source: Plain text to convert to markdown.
            syntax_highlighting: Whether to apply syntax highlighting to code blocks (default: True).
            smart_tables: Whether to format detected tables nicely (default: True).
            smart_quotes: Whether to convert quotes to typographic quotes (default: True).
            **kwargs: Additional processing options.
            
        Returns:
            Text in enhanced markdown format.
        """
        if not self._has_markitdown:
            raise ImportError("The markitdown library is required but not installed. "
                             "Install it with: pip install markitdown")
        
        # Get formatting options
        syntax_highlighting = kwargs.get('syntax_highlighting', True)
        smart_tables = kwargs.get('smart_tables', True)
        smart_quotes = kwargs.get('smart_quotes', True)
        
        # Read the source if it's a file path, or use directly if it's text
        text = self._read_source(source, **kwargs)
        
        # Configure markitdown options
        markitdown_options = {
            'syntax_highlight': syntax_highlighting,
            'smart_tables': smart_tables,
            'smart_quotes': smart_quotes,
            # Add any other options supported by markitdown
        }
        
        # Apply markitdown formatting
        formatted_text = markitdown.convert(text, **markitdown_options)
        
        # Preprocess the formatted text
        return self.preprocess(formatted_text, **kwargs)
    
    def preprocess(self, text: str, **kwargs) -> str:
        """
        Preprocess the formatted markdown text.
        
        Args:
            text: Raw formatted markdown text.
            add_toc: Whether to add a table of contents (default: False).
            toc_title: Title for the table of contents if added (default: "Table of Contents").
            **kwargs: Additional preprocessing options.
            
        Returns:
            Preprocessed markdown text.
        """
        # Get preprocessing options
        add_toc = kwargs.get('add_toc', False)
        toc_title = kwargs.get('toc_title', "Table of Contents")
        
        # Add table of contents if requested
        if add_toc and self._has_markitdown:
            toc = markitdown.generate_toc(text, title=toc_title)
            text = toc + "\n\n" + text
        
        return text
    
    def extract_metadata(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from the text if possible.
        
        Args:
            source: Text to extract metadata from.
            **kwargs: Additional options.
            
        Returns:
            Dictionary of metadata.
        """
        metadata = {}
        
        # Try to extract title from the first heading
        text = self._read_source(source, **kwargs)
        title_match = re.search(r'^# (.+)$', text, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1)
            
        # Count words and estimate reading time
        word_count = len(re.findall(r'\b\w+\b', text))
        metadata['word_count'] = word_count
        metadata['reading_time_minutes'] = round(word_count / 200)  # Assuming 200 words per minute
        
        return metadata
    
    def _read_source(self, source: str, **kwargs) -> str:
        """
        Read the source, which could be a file path or raw text.
        
        Args:
            source: File path or raw text.
            is_file: Whether the source is a file path (default: auto-detect).
            **kwargs: Additional options.
            
        Returns:
            The text content.
        """
        is_file = kwargs.get('is_file', None)
        
        # Auto-detect if source is a file
        if is_file is None:
            # If the string looks like a file path and exists, treat it as a file
            if '/' in source or '\\' in source:
                try:
                    with open(source, 'r', encoding='utf-8') as f:
                        return f.read()
                except (IOError, FileNotFoundError):
                    # Not a file or can't be read, treat as raw text
                    pass
            
            # Treat as raw text
            return source
        
        # Explicit file path
        if is_file:
            with open(source, 'r', encoding='utf-8') as f:
                return f.read()
                
        # Explicit raw text
        return source 