#!/usr/bin/env python3
"""
Basic usage examples for the DataReader package.
"""

import os
import sys
import argparse

# Add the parent directory to sys.path to import DataReader during development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datareader import DataReader

def process_pdf(file_path, output_path=None, use_pymupdf=False, use_pypdf=False, force_markitdown=False):
    """Process a PDF file."""
    print(f"Processing PDF: {file_path}")
    
    if force_markitdown:
        print("PDF Processor: Markitdown (forced)")
    elif use_pymupdf:
        print("PDF Processor: PyMuPDF (forced)")
    elif use_pypdf:
        print("PDF Processor: pypdf (forced)")
    else:
        print("PDF Processor: Auto (with fallback)")
    
    # Extract text from PDF with processor preferences
    text = DataReader.read_pdf(file_path, force_pymupdf=use_pymupdf, force_pypdf=use_pypdf, force_markitdown=force_markitdown)
    
    # Save as markdown if output path is provided
    if output_path:
        metadata = {
            'source': file_path,
            'type': 'pdf'
        }
        
        # Formatting options
        format_options = {
            'metadata': metadata,
            'add_front_matter': True
        }
        
        DataReader.save_markdown(text, output_path, **format_options)
        print(f"Markdown saved to: {output_path}")
    else:
        # Print a preview
        formatted_text = DataReader.to_markdown(text)
        preview = formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text
        
        print("\nPreview:")
        print("-" * 80)
        print(preview)
        print("-" * 80)
    
    return text

def process_url(url, output_path=None):
    """Process a URL."""
    print(f"Processing URL: {url}")
    
    # Extract text from URL
    text = DataReader.read_url(url)
    
    # Save as markdown if output path is provided
    if output_path:
        metadata = {
            'source': url,
            'type': 'web'
        }
        
        # Formatting options
        format_options = {
            'metadata': metadata,
            'add_front_matter': True
        }
        
        DataReader.save_markdown(text, output_path, **format_options)
        print(f"Markdown saved to: {output_path}")
    else:
        formatted_text = DataReader.to_markdown(text)
        preview = formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text
        
        print("\nPreview:")
        print("-" * 80)
        print(preview)
        print("-" * 80)
    
    return text

def process_video(file_path, output_path=None):
    """Process a video file."""
    print(f"Processing video: {file_path}")
    
    # Extract text from video
    text, metadata = DataReader.read_video(file_path)

    print(metadata)
    
    # Save as markdown if output path is provided
    if output_path:
        metadata = {
            'source': file_path,
            'type': 'video'
        }
        
        # Formatting options
        format_options = {
            'metadata': metadata,
            'add_front_matter': True
        }
        
        DataReader.save_markdown(text, output_path, **format_options)
        print(f"Markdown saved to: {output_path}")
    else:
        formatted_text = DataReader.to_markdown(text)
        preview = formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text
        
        print("\nPreview:")
        print("-" * 80)
        print(preview)
        print("-" * 80)
    
    return text

def process_audio(file_path, output_path=None):
    """Process an audio file."""
    print(f"Processing audio: {file_path}")
    
    # Extract text from audio
    text = DataReader.read_audio(file_path)
    
    # Save as markdown if output path is provided
    if output_path:
        metadata = {
            'source': file_path,
            'type': 'audio'
        }
        
        # Formatting options
        format_options = {
            'metadata': metadata,
            'add_front_matter': True
        }
        
        DataReader.save_markdown(text, output_path, **format_options)
        print(f"Markdown saved to: {output_path}")
    else:
        formatted_text = DataReader.to_markdown(text)
        preview = formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text
        
        print("\nPreview:")
        print("-" * 80)
        print(preview)
        print("-" * 80)
    
    return text

def main():
    """Main entry point for the example script."""
    parser = argparse.ArgumentParser(description="DataReader example usage")
    parser.add_argument("--pdf", help="Path to a PDF file to process")
    parser.add_argument("--url", help="URL to process")
    parser.add_argument("--video", help="Path to a video file to process")
    parser.add_argument("--audio", help="Path to an audio file to process")
    parser.add_argument("--youtube", help="YouTube URL to process")
    parser.add_argument("--output", help="Path to save the output markdown")
    
    # PDF processor options
    parser.add_argument("--use-pymupdf", action="store_true", help="Force using PyMuPDF for PDF processing")
    parser.add_argument("--use-pypdf", action="store_true", help="Force using pypdf for PDF processing")
    parser.add_argument("--use-markitdown", action="store_true", help="Force using markitdown for PDF processing")
    # For backwards compatibility
    parser.add_argument("--use-pypdf2", action="store_true", help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    # Handle deprecated option
    use_pypdf = args.use_pypdf or args.use_pypdf2
    
    if args.pdf:
        process_pdf(args.pdf, args.output, args.use_pymupdf, use_pypdf, args.use_markitdown)
    elif args.url:
        process_url(args.url, args.output)
    elif args.video:
        process_video(args.video, args.output)
    elif args.audio:
        process_audio(args.audio, args.output)
    elif args.youtube:
        # YouTube is processed as a video
        process_video(args.youtube, args.output)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 