import os
import tempfile
from typing import Dict, Any, Optional, List
import speech_recognition as sr
from pydub import AudioSegment

from datareader.processors.base_processor import BaseProcessor

class AudioProcessor(BaseProcessor):
    """
    Processor for extracting text from audio files through transcription.
    """
    
    def process(self, source: str, **kwargs) -> str:
        """
        Process an audio file and transcribe its content.
        
        Args:
            source: Path to the audio file.
            language: Language code for transcription (default: 'en-US').
            chunk_size: Size of audio chunks in milliseconds for processing (default: 60000).
            **kwargs: Additional processing options.
            
        Returns:
            Transcribed text from the audio.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"Audio file not found: {source}")
        
        # Get processing options
        language = kwargs.get('language', 'en-US')
        chunk_size = kwargs.get('chunk_size', 60000)  # Default 60 seconds chunks
        
        # Load audio file
        audio = self._load_audio(source)
        
        # Transcribe in chunks to handle large files
        transcription = ""
        total_duration = len(audio)
        
        for i in range(0, total_duration, chunk_size):
            # Extract chunk
            end = min(i + chunk_size, total_duration)
            chunk = audio[i:end]
            
            # Create temporary wav file for the chunk
            fd, temp_path = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            
            try:
                # Export chunk to WAV format
                chunk.export(temp_path, format="wav")
                
                # Transcribe the chunk
                chunk_text = self._transcribe_audio_file(temp_path, language)
                if chunk_text:
                    transcription += chunk_text + " "
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Preprocess the transcription
        return self.preprocess(transcription, **kwargs)
    
    def _load_audio(self, file_path: str) -> AudioSegment:
        """
        Load an audio file using pydub.
        
        Args:
            file_path: Path to the audio file.
            
        Returns:
            AudioSegment object.
        """
        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()[1:]  # Remove the dot and convert to lowercase
        
        # Load based on format
        if extension in ('mp3', 'wav', 'ogg', 'flac', 'aac'):
            return AudioSegment.from_file(file_path, format=extension)
        else:
            # Try loading as mp3 by default or let pydub detect format
            try:
                return AudioSegment.from_file(file_path)
            except Exception as e:
                raise ValueError(f"Unsupported audio format: {extension}. Error: {str(e)}")
    
    def _transcribe_audio_file(self, file_path: str, language: str) -> str:
        """
        Transcribe an audio file using speech_recognition.
        
        Args:
            file_path: Path to the audio file (WAV format).
            language: Language code for transcription.
            
        Returns:
            Transcribed text.
        """
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            
            try:
                # Try Google's speech recognition service
                return recognizer.recognize_google(audio_data, language=language)
            except sr.UnknownValueError:
                # Speech was unintelligible
                return ""
            except sr.RequestError:
                # Could not request results from Google
                try:
                    # Fall back to Sphinx (offline engine)
                    return recognizer.recognize_sphinx(audio_data)
                except:
                    # If all fails, return empty string
                    return ""
    
    def preprocess(self, text: str, **kwargs) -> str:
        """
        Preprocess the transcribed text.
        
        Args:
            text: Raw transcribed text.
            capitalize_sentences: Whether to capitalize sentences.
            **kwargs: Additional preprocessing options.
            
        Returns:
            Preprocessed text.
        """
        # Get preprocessing options
        capitalize_sentences = kwargs.get('capitalize_sentences', True)
        
        # Apply preprocessing
        if capitalize_sentences and text:
            # Split text into sentences and capitalize each one
            sentences = []
            for sentence in text.split('. '):
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                    sentences.append(sentence)
            
            text = '. '.join(sentences)
            
            # Ensure the text ends with a period if it doesn't already
            if not text.endswith('.'):
                text += '.'
        
        return text
    
    def extract_metadata(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from an audio file.
        
        Args:
            source: Path to the audio file.
            **kwargs: Additional options.
            
        Returns:
            Dictionary of audio metadata.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"Audio file not found: {source}")
        
        audio = self._load_audio(source)
        
        metadata = {
            'duration_seconds': len(audio) / 1000,
            'channels': audio.channels,
            'sample_width': audio.sample_width,
            'frame_rate': audio.frame_rate,
            'filename': os.path.basename(source),
            'path': source
        }
        
        return metadata 