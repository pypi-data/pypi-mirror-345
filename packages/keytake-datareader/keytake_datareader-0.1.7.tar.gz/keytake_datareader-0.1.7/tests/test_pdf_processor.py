import os
import unittest
from unittest.mock import patch, mock_open, MagicMock

from datareader.processors.pdf_processor import PDFProcessor

class TestPDFProcessor(unittest.TestCase):
    
    def test_init(self):
        """Test that the processor can be initialized."""
        processor = PDFProcessor()
        self.assertIsInstance(processor, PDFProcessor)
    
    @patch('pypdf.PdfReader')
    @patch('os.path.exists')
    def test_process(self, mock_exists, mock_pdf_reader):
        """Test the process method with a mock PDF."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Mock the PDF reader
        mock_reader_instance = MagicMock()
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Mock page extraction
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a test PDF page."
        mock_reader_instance.pages = [mock_page]
        
        # Create processor and process mock PDF
        processor = PDFProcessor()
        result = processor.process('data/DeepLesion_JMI_2018.pdf')
        
        # Assertions
        self.assertEqual(result, "This is a test PDF page.\n\n")
        mock_exists.assert_called_once_with('data/DeepLesion_JMI_2018.pdf')
    
    def test_preprocess(self):
        """Test the preprocess method."""
        processor = PDFProcessor()
        
        # Test with default options
        text = "Line 1\n\nLine 2\n  Line 3  "
        result = processor.preprocess(text)
        self.assertEqual(result, "Line 1\nLine 2\nLine 3")
        
        # Test with custom options
        text = "Line 1\n\nLine 2\n  Line 3  "
        result = processor.preprocess(text, remove_empty_lines=False, normalize_whitespace=False)
        self.assertEqual(result, text)

if __name__ == '__main__':
    unittest.main() 