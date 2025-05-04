#!/usr/bin/env python3
"""
Command-line interface for the DataReader package.
"""

import os
import sys
import argparse
from typing import Optional, Dict, Any

from datareader import DataReader, __version__

def main():
    """Main entry point for the DataReader CLI."""
    parser = argparse.ArgumentParser(
        description="DataReader - Extract and convert content from various sources to markdown"
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'DataReader v{__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # PDF subcommand
    pdf_parser = subparsers.add_parser('pdf', help='Process a PDF file')
    pdf_parser.add_argument('file', help='Path to the PDF file')
    pdf_parser.add_argument('-o', '--output', help='Output markdown file path')
    pdf_parser.add_argument('--pages', help='Specific pages to extract (comma-separated)', default=None)
    pdf_parser.add_argument('--use-pymupdf', action='store_true', help='Force using PyMuPDF processor (default is auto)')
    pdf_parser.add_argument('--use-pypdf', action='store_true', help='Force using pypdf processor (default is auto)')
    # Keep for backwards compatibility
    pdf_parser.add_argument('--use-pypdf2', action='store_true', help=argparse.SUPPRESS)
    
    # URL subcommand
    url_parser = subparsers.add_parser('url', help='Process a web page')
    url_parser.add_argument('url', help='URL to process')
    url_parser.add_argument('-o', '--output', help='Output markdown file path')
    
    # Video subcommand
    video_parser = subparsers.add_parser('video', help='Process a video file')
    video_parser.add_argument('file', help='Path to the video file')
    video_parser.add_argument('-o', '--output', help='Output markdown file path')
    video_parser.add_argument('--language', help='Language code for transcription', default='en-US')
    
    # YouTube subcommand
    youtube_parser = subparsers.add_parser('youtube', help='Process a YouTube video')
    youtube_parser.add_argument('url', help='YouTube URL')
    youtube_parser.add_argument('-o', '--output', help='Output markdown file path')
    youtube_parser.add_argument('--language', help='Language code for transcription', default='en-US')
    youtube_parser.add_argument('--quality', help='Video quality to download', default='360p')
    
    # Audio subcommand
    audio_parser = subparsers.add_parser('audio', help='Process an audio file')
    audio_parser.add_argument('file', help='Path to the audio file')
    audio_parser.add_argument('-o', '--output', help='Output markdown file path')
    audio_parser.add_argument('--language', help='Language code for transcription', default='en-US')
    
    # Common options for all subcommands
    for subparser in [pdf_parser, url_parser, video_parser, youtube_parser, audio_parser]:
        subparser.add_argument('--no-front-matter', action='store_true', 
                              help='Disable front matter in markdown output')
        subparser.add_argument('--use-markitdown', action='store_true',
                              help='Use enhanced markdown formatting with markitdown')
        subparser.add_argument('--syntax-highlighting', action='store_true',
                              help='Apply syntax highlighting to code blocks (requires markitdown)')
        subparser.add_argument('--smart-tables', action='store_true',
                              help='Format detected tables nicely (requires markitdown)')
        subparser.add_argument('--smart-quotes', action='store_true',
                              help='Convert quotes to typographic quotes (requires markitdown)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Process according to command
    if args.command == 'pdf':
        process_pdf(args)
    elif args.command == 'url':
        process_url(args)
    elif args.command == 'video':
        process_video(args)
    elif args.command == 'youtube':
        process_youtube(args)
    elif args.command == 'audio':
        process_audio(args)

def process_pdf(args):
    """Process a PDF file."""
    try:
        # Convert pages argument if provided
        pages = None
        if args.pages:
            pages = [int(p.strip()) for p in args.pages.split(',')]
        
        # Determine processor to use
        force_pymupdf = args.use_pymupdf
        force_pypdf = args.use_pypdf
        
        # Handle deprecated option for backwards compatibility
        if args.use_pypdf2:
            force_pypdf = True
        
        # Extract text from PDF with processor preferences
        text = DataReader.read_pdf(
            args.file, 
            pages=pages,
            force_pymupdf=force_pymupdf,
            force_pypdf=force_pypdf
        )
        
        # Save or print output with formatting options
        format_options = {
            'use_markitdown': args.use_markitdown,
            'syntax_highlighting': args.syntax_highlighting,
            'smart_tables': args.smart_tables,
            'smart_quotes': args.smart_quotes,
        }
        
        save_or_print_output(text, args.output, {
            'source': args.file,
            'type': 'pdf'
        }, not args.no_front_matter, **format_options)
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}", file=sys.stderr)
        sys.exit(1)

def process_url(args):
    """Process a URL."""
    try:
        # Extract text from URL
        text = DataReader.read_url(args.url)
        
        # Save or print output with formatting options
        format_options = {
            'use_markitdown': args.use_markitdown,
            'syntax_highlighting': args.syntax_highlighting,
            'smart_tables': args.smart_tables,
            'smart_quotes': args.smart_quotes,
        }
        
        save_or_print_output(text, args.output, {
            'source': args.url,
            'type': 'web'
        }, not args.no_front_matter, **format_options)
        
    except Exception as e:
        print(f"Error processing URL: {str(e)}", file=sys.stderr)
        sys.exit(1)

def process_video(args):
    """Process a video file."""
    try:
        # Extract text from video
        text = DataReader.read_video(args.file, language=args.language)
        
        # Save or print output with formatting options
        format_options = {
            'use_markitdown': args.use_markitdown,
            'syntax_highlighting': args.syntax_highlighting,
            'smart_tables': args.smart_tables,
            'smart_quotes': args.smart_quotes,
        }
        
        save_or_print_output(text, args.output, {
            'source': args.file,
            'type': 'video'
        }, not args.no_front_matter, **format_options)
        
    except Exception as e:
        print(f"Error processing video: {str(e)}", file=sys.stderr)
        sys.exit(1)

def process_youtube(args):
    """Process a YouTube video."""
    try:
        # Extract text from YouTube video
        text = DataReader.read_video(
            args.url, 
            language=args.language,
            youtube_quality=args.quality
        )
        
        # Save or print output with formatting options
        format_options = {
            'use_markitdown': args.use_markitdown,
            'syntax_highlighting': args.syntax_highlighting,
            'smart_tables': args.smart_tables,
            'smart_quotes': args.smart_quotes,
        }
        
        save_or_print_output(text, args.output, {
            'source': args.url,
            'type': 'youtube'
        }, not args.no_front_matter, **format_options)
        
    except Exception as e:
        print(f"Error processing YouTube video: {str(e)}", file=sys.stderr)
        sys.exit(1)

def process_audio(args):
    """Process an audio file."""
    try:
        # Extract text from audio
        text = DataReader.read_audio(args.file, language=args.language)
        
        # Save or print output with formatting options
        format_options = {
            'use_markitdown': args.use_markitdown,
            'syntax_highlighting': args.syntax_highlighting,
            'smart_tables': args.smart_tables,
            'smart_quotes': args.smart_quotes,
        }
        
        save_or_print_output(text, args.output, {
            'source': args.file,
            'type': 'audio'
        }, not args.no_front_matter, **format_options)
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}", file=sys.stderr)
        sys.exit(1)

def save_or_print_output(text: str, output_path: Optional[str], metadata: Dict[str, Any], 
                        add_front_matter: bool, **format_options):
    """
    Save the output to a file or print it to stdout.
    
    Args:
        text: The text to format and save/print.
        output_path: Path where the markdown file will be saved.
        metadata: Metadata for the front matter.
        add_front_matter: Whether to add front matter.
        **format_options: Additional formatting options.
    """
    # Combine all formatting options
    options = {
        'metadata': metadata,
        'add_front_matter': add_front_matter,
    }
    options.update(format_options)
    
    if output_path:
        # Save to file
        DataReader.save_markdown(
            text, 
            output_path, 
            **options
        )
        # Report the formatter used
        formatter_type = "Markitdown" if format_options.get('use_markitdown') else "Standard markdown"
        print(f"Output saved to: {output_path} using {formatter_type}")
    else:
        # Print to stdout
        if add_front_matter and metadata:
            print("---")
            for key, value in metadata.items():
                print(f"{key}: {value}")
            print("---")
            print()
        
        # Convert to markdown and print
        formatted_text = DataReader.to_markdown(text, **options)
        print(formatted_text)

if __name__ == "__main__":
    main() 