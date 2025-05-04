import re
from typing import Dict, Any, List
import markdown

from datareader.formatters.base_formatter import BaseFormatter

class MarkdownFormatter(BaseFormatter):
    """
    Formatter for converting text to Markdown format.
    """
    
    def format(self, text: str, **kwargs) -> str:
        """
        Format the input text as Markdown.
        
        Args:
            text: Input text to format.
            metadata: Optional metadata to include in the front matter.
            add_front_matter: Whether to add YAML front matter (default: False).
            headings_level: Base level for headings (default: 1).
            detect_headings: Whether to try to detect and format headings (default: True).
            detect_lists: Whether to try to detect and format lists (default: True).
            **kwargs: Additional formatting options.
            
        Returns:
            Text formatted in Markdown.
        """
        # Get formatting options
        metadata = kwargs.get('metadata', {})
        add_front_matter = kwargs.get('add_front_matter', False)
        headings_level = kwargs.get('headings_level', 1)
        detect_headings = kwargs.get('detect_headings', True)
        detect_lists = kwargs.get('detect_lists', True)
        
        # Start with clean text
        formatted_text = text.strip()
        
        # Apply Markdown formatting
        if detect_headings:
            formatted_text = self._format_headings(formatted_text, headings_level)
            
        if detect_lists:
            formatted_text = self._format_lists(formatted_text)
        
        # Add front matter if requested
        if add_front_matter and metadata:
            front_matter = "---\n"
            for key, value in metadata.items():
                front_matter += f"{key}: {value}\n"
            front_matter += "---\n\n"
            formatted_text = front_matter + formatted_text
            
        return formatted_text
    
    def _format_headings(self, text: str, base_level: int = 1) -> str:
        """
        Detect and format headings in the text.
        
        Args:
            text: Input text.
            base_level: Base level for headings (1-6).
            
        Returns:
            Text with Markdown headings.
        """
        lines = text.split('\n')
        formatted_lines = []
        
        # Regex patterns for potential headings
        heading_patterns = [
            # All caps followed by colon or newline
            r'^([A-Z][A-Z\s]+)(?::|\n|$)',
            # Numbered section (e.g., "1. Title")
            r'^(\d+\.\s+\w.+)$',
            # Short sentences (3-5 words) that might be titles
            r'^([^\.\n]{5,50})$'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            is_heading = False
            
            # Skip if already a Markdown heading
            if line_stripped.startswith('#'):
                formatted_lines.append(line)
                continue
                
            # Check if this looks like a heading
            for pattern in heading_patterns:
                if re.match(pattern, line_stripped):
                    # Don't convert very long lines
                    if len(line_stripped) <= 100:
                        hashes = '#' * base_level
                        formatted_lines.append(f"{hashes} {line_stripped}")
                        is_heading = True
                        break
            
            if not is_heading:
                formatted_lines.append(line)
                
        return '\n'.join(formatted_lines)
    
    def _format_lists(self, text: str) -> str:
        """
        Detect and format lists in the text.
        
        Args:
            text: Input text.
            
        Returns:
            Text with Markdown lists.
        """
        lines = text.split('\n')
        formatted_lines = []
        
        # Regex patterns for potential list items
        list_patterns = [
            # Numbered list items (1., 2., etc.)
            (r'^(\d+)\.\s+(.+)$', '{}. {}'),
            # Bullet list items (*, -, •)
            (r'^[•\*\-]\s+(.+)$', '* {}'),
            # Lettered list items (a., b., etc.)
            (r'^([a-z])\.\s+(.+)$', '{}. {}')
        ]
        
        for line in lines:
            line_stripped = line.strip()
            is_list_item = False
            
            # Skip if already a Markdown list item
            if line_stripped.startswith('* ') or re.match(r'^\d+\.\s+', line_stripped):
                formatted_lines.append(line)
                continue
                
            # Check if this looks like a list item
            for pattern, template in list_patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    if len(match.groups()) == 1:
                        formatted_lines.append(template.format(match.group(1)))
                    elif len(match.groups()) == 2:
                        formatted_lines.append(template.format(match.group(1), match.group(2)))
                    is_list_item = True
                    break
            
            if not is_list_item:
                formatted_lines.append(line)
                
        return '\n'.join(formatted_lines)
    
    def html_to_markdown(self, html_text: str) -> str:
        """
        Convert HTML to Markdown.
        
        Args:
            html_text: HTML text to convert.
            
        Returns:
            Markdown version of the HTML.
        """
        # This method could be expanded with a more sophisticated HTML to Markdown converter
        # For now, we'll use a simple approach
        
        # Remove HTML tags (simplistic approach)
        no_tags = re.sub(r'<[^>]+>', '', html_text)
        
        # Fix common entities
        entities_map = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
        }
        
        for entity, replacement in entities_map.items():
            no_tags = no_tags.replace(entity, replacement)
            
        return no_tags.strip() 