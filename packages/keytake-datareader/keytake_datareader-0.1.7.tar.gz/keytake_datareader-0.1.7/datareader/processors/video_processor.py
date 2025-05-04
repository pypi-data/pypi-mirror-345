import os
import tempfile
import asyncio
from typing import Dict, Any, Optional
import speech_recognition as sr
from pydub import AudioSegment
import yt_dlp
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable, NoTranscriptFound

# Try different import paths for moviepy based on version
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError:
        VideoFileClip = None
        print("Warning: MoviePy's VideoFileClip could not be imported. Video processing capabilities will be limited.")

from datareader.processors.base_processor import BaseProcessor
from datareader.processors.audio_processor import AudioProcessor

class VideoProcessor(BaseProcessor):
    """
    Processor for extracting text from video files through transcription.
    """
    
    def process(self, source: str, **kwargs) -> str:
        """
        Process a video file or YouTube URL and extract its audio content as text.
        
        Args:
            source: Path to video file or YouTube URL.
            language: Language code for transcription (default: 'en-US').
            chunk_size: Size of audio chunks in milliseconds for processing (default: 60000).
            **kwargs: Additional processing options.
            
        Returns:
            Transcribed text from the video.
        """
        is_youtube = source.startswith(('http://', 'https://')) and ('youtube.com' in source or 'youtu.be' in source)
        
        if is_youtube:
            # Try to get YouTube transcript directly first
            try:
                text = self._get_youtube_transcript(source, **kwargs)
                metadata = self.extract_metadata(source, **kwargs)
                if text and metadata:
                    return text, metadata
            except Exception as e:
                print(f"Could not get transcript directly: {str(e)}")
            
            # Fall back to audio transcription
            temp_video_file = self._download_youtube_video(source, **kwargs)
            try:
                return self._process_video_file(temp_video_file, **kwargs)
            finally:
                # Clean up temporary file
                if os.path.exists(temp_video_file):
                    os.remove(temp_video_file)
        else:
            # Process local video file
            if not os.path.exists(source):
                raise FileNotFoundError(f"Video file not found: {source}")
            
            return self._process_video_file(source, **kwargs)
    
    def _extract_video_id(self, url: str) -> str:
        """
        Extract YouTube video ID from URL.
        
        Args:
            url: YouTube URL.
            
        Returns:
            YouTube video ID.
        """
        if "youtube.com" in url:
            return url.split("v=")[-1].split("&")[0]
        elif "youtu.be" in url:
            return url.split("/")[-1]
        else:
            raise ValueError(f"Not a valid YouTube URL: {url}")
    
    def _get_youtube_transcript(self, url: str, **kwargs) -> str:
        """
        Get YouTube transcript using YouTubeTranscriptApi.
        
        Args:
            url: YouTube URL.
            languages: List of language codes to try (default: ['en']).
            
        Returns:
            Transcript text or None if not available.
        """
        languages = kwargs.get('languages', ['en', 'fr', 'vi', 'de'])
        video_id = self._extract_video_id(url)
        
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            transcript = " ".join([entry['text'] for entry in transcript_data])
            return transcript
        except (TranscriptsDisabled, VideoUnavailable, NoTranscriptFound) as e:
            print(f"YouTube transcript not available: {str(e)}")
            return None
    
    def _download_youtube_video(self, url: str, **kwargs) -> str:
        """
        Download a YouTube video using yt-dlp.
        
        Args:
            url: YouTube URL.
            
        Returns:
            Path to the downloaded video file.
        """
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.mp4')
        os.close(fd)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'mp4[height<=360]/mp4/best',
            'outtmpl': temp_path,
            'quiet': True,
        }
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return temp_path
    
    def _process_video_file(self, video_path: str, **kwargs) -> str:
        """
        Process a video file by extracting its audio and transcribing it.
        
        Args:
            video_path: Path to the video file.
            **kwargs: Additional processing options.
            
        Returns:
            Transcribed text from the video.
        """
        # Create temporary audio file
        fd, temp_audio_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        try:
            # Extract audio from video
            if VideoFileClip is not None:
                # Use moviepy if available
                video = VideoFileClip(video_path)
                video.audio.write_audiofile(temp_audio_path, logger=None)
            else:
                # Fallback to ffmpeg directly
                import subprocess
                cmd = [
                    'ffmpeg', '-i', video_path, 
                    '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
                    temp_audio_path, '-y', '-loglevel', 'quiet'
                ]
                subprocess.run(cmd, check=True)
            
            # Use the audio processor to transcribe the audio
            audio_processor = AudioProcessor()
            return audio_processor.process(temp_audio_path, **kwargs)
        except Exception as e:
            print(f"Error processing video file: {str(e)}")
            raise
        finally:
            # Clean up temporary audio file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    
    def extract_metadata(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from a video file.
        
        Args:
            source: Path to the video file or YouTube URL.
            **kwargs: Additional options.
            
        Returns:
            Dictionary of video metadata.
        """
        metadata = {}
        
        is_youtube = source.startswith(('http://', 'https://')) and ('youtube.com' in source or 'youtu.be' in source)
        
        if is_youtube:
            # Extract YouTube metadata using yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(source, download=False)
                
                metadata = {
                    'title': info_dict.get('title'),
                    'uploader': info_dict.get('uploader'),
                    'duration': info_dict.get('duration'),
                    'view_count': info_dict.get('view_count'),
                    'average_rating': info_dict.get('average_rating'),
                    'upload_date': info_dict.get('upload_date'),
                    'description': info_dict.get('description'),
                    'categories': info_dict.get('categories'),
                    'tags': info_dict.get('tags'),
                    'channel_id': info_dict.get('channel_id'),
                    'channel_url': info_dict.get('channel_url'),
                    'url': source
                }
        else:
            # Extract local video metadata
            if not os.path.exists(source):
                raise FileNotFoundError(f"Video file not found: {source}")
            
            if VideoFileClip is not None:
                # Use moviepy if available
                clip = VideoFileClip(source)
                metadata = {
                    'duration': clip.duration,
                    'fps': clip.fps,
                    'size': clip.size,
                    'filename': os.path.basename(source),
                    'path': source
                }
                clip.close()
            else:
                # Use ffprobe as a fallback
                try:
                    import subprocess
                    import json
                    cmd = [
                        'ffprobe', '-v', 'quiet', '-print_format', 'json',
                        '-show_format', '-show_streams', source
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    info = json.loads(result.stdout)
                    
                    # Get video stream
                    video_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
                    
                    metadata = {
                        'filename': os.path.basename(source),
                        'path': source,
                        'format': info.get('format', {}).get('format_name'),
                        'duration': float(info.get('format', {}).get('duration', 0)),
                    }
                    
                    if video_stream:
                        metadata.update({
                            'width': video_stream.get('width'),
                            'height': video_stream.get('height'),
                            'fps': eval(video_stream.get('r_frame_rate', '0/1')), # convert "24/1" to 24
                            'codec': video_stream.get('codec_name')
                        })
                except Exception as e:
                    print(f"Error extracting video metadata with ffprobe: {str(e)}")
                    # Provide basic metadata at minimum
                    metadata = {
                        'filename': os.path.basename(source),
                        'path': source,
                        'filesize': os.path.getsize(source),
                    }
            
        return metadata 