import os
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

from datareader.processors.pdf_processor import PDFProcessor
from datareader.processors.pymupdf_processor import PyMuPDFProcessor
from datareader.processors.url_processor import URLProcessor
from datareader.processors.video_processor import VideoProcessor
from datareader.processors.audio_processor import AudioProcessor
from datareader.processors.markitdown_processor import MarkitdownProcessor
from datareader.formatters.markdown_formatter import MarkdownFormatter

class DataReader:
    """
    Main class for reading and processing data from various sources.
    """
    
    @staticmethod
    def read_pdf(file_path: str, **kwargs) -> str:
        """
        Read and preprocess a PDF file.
        
        This method will try processors in this order:
        1. PyMuPDF for better performance and features
        2. pypdf as a fallback
        3. markitdown as a final fallback
        
        Args:
            file_path: Path to the PDF file.
            force_pymupdf: Force using PyMuPDF even if it would normally fall back.
            force_pypdf: Force using pypdf even if PyMuPDF would normally work.
            force_markitdown: Force using markitdown even if other processors would normally work.
            **kwargs: Additional options to pass to the PDF processor.
            
        Returns:
            Extracted text in plain format.
        """
        # Check user preferences for which processor to use
        force_pymupdf = kwargs.pop('force_pymupdf', False)
        force_pypdf = kwargs.pop('force_pypdf', False)
        force_markitdown = kwargs.pop('force_markitdown', False)
        
        # For backwards compatibility
        if 'force_pypdf2' in kwargs:
            force_pypdf = kwargs.pop('force_pypdf2', False)
        
        # If multiple processors are forced, set priority
        if sum([force_pymupdf, force_pypdf, force_markitdown]) > 1:
            # Priority: pymupdf > pypdf > markitdown
            if force_pymupdf:
                force_pypdf = False
                force_markitdown = False
            elif force_pypdf:
                force_markitdown = False
        
        extracted_text = ""
        errors = []
        
        # Try PyMuPDF first unless another processor is forced
        if not force_pypdf and not force_markitdown:
            try:
                processor = PyMuPDFProcessor()
                extracted_text = processor.process(file_path, **kwargs)
                return extracted_text
            except Exception as e:
                errors.append(f"PyMuPDF error: {str(e)}")
                if force_pymupdf:
                    # If PyMuPDF was forced but failed, don't fall back
                    raise RuntimeError(f"PyMuPDF processing failed and fallback disabled: {str(e)}")
        
        # Try pypdf if PyMuPDF failed or was skipped and markitdown isn't forced
        if not force_markitdown:
            try:
                processor = PDFProcessor()
                extracted_text = processor.process(file_path, **kwargs)
                return extracted_text
            except Exception as e:
                errors.append(f"pypdf error: {str(e)}")
                if force_pypdf:
                    # If pypdf was forced but failed, don't fall back
                    raise RuntimeError(f"pypdf processing failed and fallback disabled: {str(e)}")
        
        # Try markitdown as a final fallback
        try:
            # First try to extract text with either processor to pass to markitdown
            if not errors:  # If we haven't tried any processor yet
                try:
                    processor = PyMuPDFProcessor()
                    raw_text = processor.process(file_path, **kwargs)
                except Exception:
                    try:
                        processor = PDFProcessor()
                        raw_text = processor.process(file_path, **kwargs)
                    except Exception:
                        # If both fail to extract text, we can't proceed with markitdown
                        raise RuntimeError("Could not extract text for markitdown processing")
            else:
                # Use a simple text extraction method here
                with open(file_path, 'rb') as f:
                    raw_text = f.read().decode('utf-8', errors='ignore')
            
            # Process the extracted text with markitdown
            processor = MarkitdownProcessor()
            extracted_text = processor.process(raw_text, **kwargs)
            return extracted_text
        except Exception as e:
            errors.append(f"markitdown error: {str(e)}")
            
            # If we get here, all processors failed
            error_msg = "All PDF processors failed:\n" + "\n".join(errors)
            raise RuntimeError(error_msg)
    
    @staticmethod
    def read_url(url: str, **kwargs) -> str:
        """
        Read and preprocess content from a URL.
        
        Args:
            url: URL to scrape.
            **kwargs: Additional options to pass to the URL processor.
            
        Returns:
            Extracted text in plain format.
        """
        processor = URLProcessor()
        return processor.process(url, **kwargs)
    
    @staticmethod
    def read_video(file_path: str, **kwargs) -> str:
        """
        Read and transcribe a video file.
        
        Args:
            file_path: Path to the video file.
            **kwargs: Additional options to pass to the video processor.
            
        Returns:
            Transcribed text in plain format.
        """
        processor = VideoProcessor()
        return processor.process(file_path, **kwargs)
    
    @staticmethod
    def read_audio(file_path: str, **kwargs) -> str:
        """
        Read and transcribe an audio file.
        
        Args:
            file_path: Path to the audio file.
            **kwargs: Additional options to pass to the audio processor.
            
        Returns:
            Transcribed text in plain format.
        """
        processor = AudioProcessor()
        return processor.process(file_path, **kwargs)
    
    @staticmethod
    def save_markdown(text: str, output_path: str, **kwargs) -> None:
        """
        Save processed text as a markdown file.
        
        Args:
            text: The text to format and save.
            output_path: Path where the markdown file will be saved.
            **kwargs: Additional formatting options.
        """
        # Use only standard markdown formatter
        formatter = MarkdownFormatter()
            
        markdown_text = formatter.format(text, **kwargs)
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
            
    @staticmethod
    def to_markdown(text: str, **kwargs) -> str:
        """
        Convert processed text to markdown format without saving to a file.
        
        Args:
            text: The text to format.
            **kwargs: Additional formatting options.
            
        Returns:
            Text in markdown format.
        """
        # Use only standard markdown formatter
        formatter = MarkdownFormatter()
            
        return formatter.format(text, **kwargs) 