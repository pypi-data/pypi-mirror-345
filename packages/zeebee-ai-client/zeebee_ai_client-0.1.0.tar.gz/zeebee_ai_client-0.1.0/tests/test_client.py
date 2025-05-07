"""
Tests for the ZeebeeClient class.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from zeebee_ai_client import ZeebeeClient
from zeebee_ai_client.exceptions import AuthenticationError

class TestZeebeeClient:
    """Test suite for ZeebeeClient"""
    
    def test_init_with_api_key(self):
        """Test client initialization with API key"""
        client = ZeebeeClient(api_key="test-api-key")
        assert client.api_key == "test-api-key"
        
    def test_init_with_env_var(self):
        """Test client initialization with environment variable"""
        with patch.dict(os.environ, {"ZEEBEE_API_KEY": "env-api-key"}):
            client = ZeebeeClient()
            assert client.api_key == "env-api-key"
            
    @patch("requests.post")
    def test_chat(self, mock_post):
        """Test chat method"""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "Hello!",
            "conversation_id": "test-convo-id"
        }
        mock_post.return_value = mock_response
        
        # Test
        client = ZeebeeClient(api_key="test-api-key")
        result = client.chat(message="Hi", model="gpt-4o")
        
        # Assertions
        mock_post.assert_called_once()
        assert result["response"] == "Hello!"
        assert result["conversation_id"] == "test-convo-id"
