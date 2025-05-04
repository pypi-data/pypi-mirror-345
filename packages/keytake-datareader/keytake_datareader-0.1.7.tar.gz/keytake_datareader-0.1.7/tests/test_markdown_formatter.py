import unittest

from datareader.formatters.markdown_formatter import MarkdownFormatter

class TestMarkdownFormatter(unittest.TestCase):
    
    def test_init(self):
        """Test that the formatter can be initialized."""
        formatter = MarkdownFormatter()
        self.assertIsInstance(formatter, MarkdownFormatter)
    
    def test_format_basic(self):
        """Test basic formatting without special options."""
        formatter = MarkdownFormatter()
        
        text = "This is a test."
        result = formatter.format(text)
        
        self.assertEqual(result, text)
    
    def test_format_with_front_matter(self):
        """Test formatting with front matter."""
        formatter = MarkdownFormatter()
        
        text = "This is a test."
        metadata = {
            'title': 'Test Document',
            'author': 'Test Author'
        }
        
        result = formatter.format(text, metadata=metadata, add_front_matter=True)
        
        expected = "---\ntitle: Test Document\nauthor: Test Author\n---\n\nThis is a test."
        self.assertEqual(result, expected)
    
    def test_format_headings(self):
        """Test heading detection and formatting."""
        formatter = MarkdownFormatter()
        
        text = "INTRODUCTION\nThis is a test.\nSECTION 1\nMore text here."
        
        result = formatter.format(text, detect_headings=True)
        
        expected = "# INTRODUCTION\nThis is a test.\n# SECTION 1\nMore text here."
        self.assertEqual(result, expected)
    
    def test_format_lists(self):
        """Test list detection and formatting."""
        formatter = MarkdownFormatter()
        
        text = "Items:\n1. First item\n2. Second item\n• Bullet point\na. Sub item"
        
        result = formatter.format(text, detect_lists=True)
        
        expected = "Items:\n1. First item\n2. Second item\n* Bullet point\na. Sub item"
        self.assertEqual(result, expected)
    
    def test_html_to_markdown(self):
        """Test HTML to Markdown conversion."""
        formatter = MarkdownFormatter()
        
        html = "<p>This is <strong>bold</strong> text with an <a href='link'>anchor</a>.</p>"
        
        result = formatter.html_to_markdown(html)
        
        # This is a simple implementation so we just check basic tag removal
        expected = "This is bold text with an anchor."
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main() 