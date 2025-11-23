import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import os

# Import the router and app
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from routers.practice import router
from schemas.tts import TTSRequest

# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestTTSEndpoint:
    """Test suite for the /api/tts endpoint"""
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key_123"})
    @patch('routers.practice.FishAudio')
    def test_tts_success_with_bytes(self, mock_fish_audio_class):
        """Test successful TTS generation when SDK returns bytes"""
        # Mock the Fish Audio SDK
        mock_client = MagicMock()
        mock_fish_audio_class.return_value = mock_client
        
        # Mock audio response as bytes
        mock_audio = b"fake_audio_data_mp3_content"
        mock_client.tts.convert.return_value = mock_audio
        
        # Make request
        response = client.post(
            "/api/tts",
            json={
                "transcript": "Hello, this is a test",
                "model_id": "test_model_id_123"
            }
        )
        
        # Assertions
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.headers["content-disposition"] == "attachment; filename=speech.mp3"
        assert response.content == mock_audio
        
        # Verify SDK was called correctly
        mock_fish_audio_class.assert_called_once_with(api_key="test_api_key_123")
        mock_client.tts.convert.assert_called_once_with(
            text="Hello, this is a test",
            reference_id="test_model_id_123"
        )
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key_123"})
    @patch('routers.practice.FishAudio')
    def test_tts_success_with_file_like_object(self, mock_fish_audio_class):
        """Test successful TTS generation when SDK returns file-like object"""
        # Mock the Fish Audio SDK
        mock_client = MagicMock()
        mock_fish_audio_class.return_value = mock_client
        
        # Mock audio response as file-like object
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_audio_from_file"
        mock_client.tts.convert.return_value = mock_file
        
        # Make request
        response = client.post(
            "/api/tts",
            json={
                "transcript": "Test transcript",
                "model_id": "model_456"
            }
        )
        
        # Assertions
        assert response.status_code == 200
        assert response.content == b"fake_audio_from_file"
        mock_file.read.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_tts_missing_api_key(self):
        """Test that missing API key returns 500 error"""
        response = client.post(
            "/api/tts",
            json={
                "transcript": "Hello",
                "model_id": "test_model"
            }
        )
        
        assert response.status_code == 500
        assert "FISH_AUDIO_API_KEY" in response.json()["detail"]
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key"})
    def test_tts_empty_transcript(self):
        """Test that empty transcript returns 400 error"""
        response = client.post(
            "/api/tts",
            json={
                "transcript": "   ",  # Only whitespace
                "model_id": "test_model"
            }
        )
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key"})
    def test_tts_empty_model_id(self):
        """Test that empty model_id returns 400 error"""
        response = client.post(
            "/api/tts",
            json={
                "transcript": "Hello world",
                "model_id": "   "  # Only whitespace
            }
        )
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key"})
    def test_tts_missing_transcript_field(self):
        """Test that missing transcript field returns 422 validation error"""
        response = client.post(
            "/api/tts",
            json={
                "model_id": "test_model"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key"})
    def test_tts_missing_model_id_field(self):
        """Test that missing model_id field returns 422 validation error"""
        response = client.post(
            "/api/tts",
            json={
                "transcript": "Hello"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key_123"})
    @patch('routers.practice.FishAudio')
    def test_tts_sdk_exception(self, mock_fish_audio_class):
        """Test handling of SDK exceptions"""
        # Mock the Fish Audio SDK to raise an exception
        mock_client = MagicMock()
        mock_fish_audio_class.return_value = mock_client
        mock_client.tts.convert.side_effect = Exception("SDK connection error")
        
        # Make request
        response = client.post(
            "/api/tts",
            json={
                "transcript": "Hello",
                "model_id": "test_model"
            }
        )
        
        # Should return 500 with error message
        assert response.status_code == 500
        assert "Error generating speech" in response.json()["detail"]
    
    @patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "test_api_key_123"})
    @patch('routers.practice.FishAudio')
    def test_tts_with_cloned_model_id(self, mock_fish_audio_class):
        """Test that cloned model ID is correctly passed to SDK"""
        # Mock the Fish Audio SDK
        mock_client = MagicMock()
        mock_fish_audio_class.return_value = mock_client
        mock_client.tts.convert.return_value = b"audio_data"
        
        # Use a realistic cloned model ID
        cloned_model_id = "cloned_voice_model_abc123xyz"
        
        response = client.post(
            "/api/tts",
            json={
                "transcript": "This is my cloned voice speaking",
                "model_id": cloned_model_id
            }
        )
        
        assert response.status_code == 200
        # Verify the cloned model ID was passed as reference_id
        mock_client.tts.convert.assert_called_once_with(
            text="This is my cloned voice speaking",
            reference_id=cloned_model_id
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

