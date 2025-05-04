import os
import unittest
from unittest.mock import patch, MagicMock

from datareader.processors.video_processor import VideoProcessor

class TestVideoProcessor(unittest.TestCase):
    
    def test_init(self):
        """Test that the processor can be initialized."""
        processor = VideoProcessor()
        self.assertIsInstance(processor, VideoProcessor)
    
    def test_extract_video_id(self):
        """Test the _extract_video_id method with different URL formats."""
        processor = VideoProcessor()
        
        # Test YouTube URLs
        self.assertEqual(processor._extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(processor._extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ&t=10s"), "dQw4w9WgXcQ")
        self.assertEqual(processor._extract_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        
        # Test invalid URL
        with self.assertRaises(ValueError):
            processor._extract_video_id("https://example.com")
    
    @patch('datareader.processors.video_processor.YouTubeTranscriptApi')
    def test_get_youtube_transcript(self, mock_transcript_api):
        """Test the _get_youtube_transcript method."""
        # Setup mock
        mock_transcript_api.get_transcript.return_value = [
            {'text': 'This is', 'start': 0.0, 'duration': 1.0},
            {'text': 'a test', 'start': 1.0, 'duration': 1.0},
            {'text': 'transcript', 'start': 2.0, 'duration': 1.0}
        ]
        
        processor = VideoProcessor()
        result = processor._get_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        self.assertEqual(result, "This is a test transcript")
        mock_transcript_api.get_transcript.assert_called_once_with("dQw4w9WgXcQ", languages=['en', 'fr', 'vi', 'de'])
    
    @patch('datareader.processors.video_processor.YoutubeDL')
    def test_download_youtube_video(self, mock_ydl):
        """Test the _download_youtube_video method."""
        # Setup mock
        mock_ydl_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        processor = VideoProcessor()
        
        with patch('tempfile.mkstemp', return_value=(1, '/tmp/test.mp4')):
            with patch('os.close') as mock_close:
                result = processor._download_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                
                self.assertEqual(result, '/tmp/test.mp4')
                mock_close.assert_called_once_with(1)
                mock_ydl_instance.download.assert_called_once_with(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
    
    @patch('datareader.processors.video_processor.VideoFileClip')
    @patch('datareader.processors.video_processor.AudioProcessor')
    def test_process_video_file_with_moviepy(self, mock_audio_processor, mock_video_file_clip):
        """Test the _process_video_file method with moviepy available."""
        # Setup mocks
        mock_video = MagicMock()
        mock_video_file_clip.return_value = mock_video
        
        mock_processor = MagicMock()
        mock_processor.process.return_value = "Transcribed test audio"
        mock_audio_processor.return_value = mock_processor
        
        processor = VideoProcessor()
        
        with patch('tempfile.mkstemp', return_value=(1, '/tmp/test.wav')):
            with patch('os.close'):
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove'):
                        result = processor._process_video_file('/fake/video.mp4')
                        
                        self.assertEqual(result, "Transcribed test audio")
                        mock_video.audio.write_audiofile.assert_called_once()
                        mock_processor.process.assert_called_once()
    
    @patch('datareader.processors.video_processor.VideoFileClip', None)  # Simulate moviepy not available
    @patch('datareader.processors.video_processor.subprocess')
    @patch('datareader.processors.video_processor.AudioProcessor')
    def test_process_video_file_with_ffmpeg(self, mock_audio_processor, mock_subprocess):
        """Test the _process_video_file method with ffmpeg fallback."""
        # Setup mocks
        mock_processor = MagicMock()
        mock_processor.process.return_value = "Transcribed test audio"
        mock_audio_processor.return_value = mock_processor
        
        processor = VideoProcessor()
        
        with patch('tempfile.mkstemp', return_value=(1, '/tmp/test.wav')):
            with patch('os.close'):
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove'):
                        result = processor._process_video_file('/fake/video.mp4')
                        
                        self.assertEqual(result, "Transcribed test audio")
                        mock_subprocess.run.assert_called_once()
                        mock_processor.process.assert_called_once()
    
    @patch('datareader.processors.video_processor._get_youtube_transcript')
    @patch('datareader.processors.video_processor._download_youtube_video')
    def test_process_youtube_url(self, mock_download, mock_transcript):
        """Test the process method with a YouTube URL."""
        # Setup mocks
        mock_transcript.return_value = "Test YouTube transcript"
        
        processor = VideoProcessor()
        
        # Mock the methods being called
        processor._get_youtube_transcript = mock_transcript
        processor._download_youtube_video = mock_download
        
        # Test with transcript available
        result = processor.process("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        self.assertEqual(result, "Test YouTube transcript")
        mock_transcript.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_download.assert_not_called()
    
    @patch('datareader.processors.video_processor.YoutubeDL')
    def test_extract_metadata_youtube(self, mock_ydl):
        """Test the extract_metadata method with a YouTube URL."""
        # Setup mock
        mock_info = {
            'title': 'Test Video',
            'uploader': 'Test Uploader',
            'duration': 123,
            'view_count': 1000,
            'upload_date': '20230101'
        }
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = mock_info
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        processor = VideoProcessor()
        result = processor.extract_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        self.assertEqual(result['title'], 'Test Video')
        self.assertEqual(result['uploader'], 'Test Uploader')
        self.assertEqual(result['duration'], 123)
        mock_ydl_instance.extract_info.assert_called_once()
    
    @patch('datareader.processors.video_processor.VideoFileClip')
    def test_extract_metadata_local(self, mock_video_file_clip):
        """Test the extract_metadata method with a local file."""
        # Setup mock
        mock_video = MagicMock()
        mock_video.duration = 60
        mock_video.fps = 30
        mock_video.size = (1920, 1080)
        mock_video_file_clip.return_value = mock_video
        
        processor = VideoProcessor()
        
        with patch('os.path.exists', return_value=True):
            result = processor.extract_metadata('/fake/video.mp4')
            
            self.assertEqual(result['duration'], 60)
            self.assertEqual(result['fps'], 30)
            self.assertEqual(result['size'], (1920, 1080))
            self.assertEqual(result['filename'], 'video.mp4')

if __name__ == '__main__':
    unittest.main() 