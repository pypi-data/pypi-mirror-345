"""
Python Client SDK for Zeebee AI Chat Platform.

This module provides a simple client for interacting with the Zeebee AI Chat API.
It supports:
- Text chat
- Voice chat via WebSocket
- Session management
- Response formatting
"""

import json
import requests
import time
import uuid
import logging
import os
from typing import Dict, List, Any, Optional, Union, Generator, Callable
import asyncio
import websockets

from .exceptions import AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)

class ZeebeeClient:
    """
    Client for the Zeebee AI Chat Platform.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://zeebee.ai",
        version: str = "v1",
        timeout: int = 60,
        debug: bool = False
    ):
        """
        Initialize the Zeebee client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            version: API version
            timeout: Request timeout in seconds
            debug: Enable debug logging
        """
        self.api_key = api_key or os.environ.get("ZEEBEE_API_KEY")
        self.base_url = base_url
        self.version = version
        self.timeout = timeout
        
        # Configure logging
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Initialize session
        self.session_id = str(uuid.uuid4())
        self.conversations = {}
        
        # Validate API key
        if not self.api_key:
            logger.warning("No API key provided. Some functionality may be limited.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"zeebee-python-sdk/{self.version}",
            "X-Session-ID": self.session_id
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"error": response.text}
            
        error_message = error_data.get("error", "Unknown error")
        
        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed: {error_message}")
        elif response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded: {error_message}")
        else:
            response.raise_for_status()
    
    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        model: str = "gpt-4o",
        system_prompt: Optional[str] = None,
        template_name: Optional[str] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        layout: Optional[str] = None
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Send a message to the chat API.
        
        Args:
            message: User message
            conversation_id: Optional ID for continuing a conversation
            model: LLM model to use
            system_prompt: Optional system prompt
            template_name: Optional template name
            template_variables: Optional template variables
            stream: Whether to stream the response
            layout: Response layout name
            
        Returns:
            Response as dict or generator of response chunks
        """
        endpoint = f"{self.base_url}/{self.version}/chat"
        
        payload = {
            "message": message,
            "model": model,
            "stream": stream
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        if system_prompt:
            payload["system_prompt"] = system_prompt
            
        if template_name:
            payload["template"] = {
                "name": template_name,
                "variables": template_variables or {}
            }
            
        if layout:
            payload["layout"] = layout
        
        if stream:
            return self._stream_chat(endpoint, payload)
        else:
            return self._send_chat(endpoint, payload)
    
    def _send_chat(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a chat request."""
        try:
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            self._handle_error_response(response)
            
            result = response.json()
            
            # Store conversation ID
            if result.get("conversation_id"):
                self.conversations[result["conversation_id"]] = {
                    "model": payload.get("model"),
                    "last_message": payload.get("message"),
                    "updated_at": time.time()
                }
                
            return result
            
        except requests.RequestException as e:
            logger.error(f"Chat request failed: {e}")
            raise
    
    def _stream_chat(self, endpoint: str, payload: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """Stream a chat response."""
        try:
            with requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout,
                stream=True
            ) as response:
                self._handle_error_response(response)
                
                # Process the streamed response
                conversation_id = None
                
                for line in response.iter_lines():
                    if not line:
                        continue
                        
                    try:
                        # Parse the JSON chunk
                        chunk = json.loads(line.decode('utf-8').lstrip('data: '))
                        
                        # Store conversation ID
                        if chunk.get("conversation_id") and not conversation_id:
                            conversation_id = chunk["conversation_id"]
                            self.conversations[conversation_id] = {
                                "model": payload.get("model"),
                                "last_message": payload.get("message"),
                                "updated_at": time.time()
                            }
                            
                        yield chunk
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in stream: {line}")
                    
        except requests.RequestException as e:
            logger.error(f"Chat stream request failed: {e}")
            raise
    
    async def voice_chat(
        self,
        audio_source: Union[str, bytes],
        conversation_id: Optional[str] = None,
        model: str = "gpt-4o",
        stream_handler: Optional[Callable[[Union[str, bytes]], None]] = None
    ) -> Dict[str, Any]:
        """
        Send a voice message and receive a voice response.
        
        Args:
            audio_source: Path to audio file or audio bytes
            conversation_id: Optional ID for continuing a conversation
            model: LLM model to use
            stream_handler: Optional handler for streaming response chunks
            
        Returns:
            Response metadata
        """
        # Prepare WebSocket URL
        ws_url = f"{self.base_url.replace('http', 'ws')}/{self.version}/voice-chat"
        
        # Read audio file if a path was provided
        if isinstance(audio_source, str):
            with open(audio_source, 'rb') as f:
                audio_data = f.read()
        else:
            audio_data = audio_source
        
        # Connect to WebSocket
        async with websockets.connect(ws_url, extra_headers=self._get_headers()) as ws:
            # Send initial message with metadata
            await ws.send(json.dumps({
                "type": "metadata",
                "conversation_id": conversation_id,
                "model": model
            }))
            
            # Send audio data
            await ws.send(audio_data)
            
            # Signal end of audio
            await ws.send(json.dumps({"type": "end_of_audio"}))
            
            # Process response
            response_chunks = []
            response_text = ""
            while True:
                message = await ws.recv()
                
                # Handle binary audio data
                if isinstance(message, bytes):
                    response_chunks.append(message)
                    if stream_handler:
                        await stream_handler(message)
                    continue
                
                # Handle JSON metadata
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "text":
                        # Add to transcribed text
                        response_text += data.get("text", "")
                        
                    elif data.get("type") == "end_of_response":
                        # End of response
                        break
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in WebSocket message: {message}")
            
            # Combine all audio chunks
            full_audio = b''.join(response_chunks)
            
            return {
                "conversation_id": conversation_id,
                "text": response_text,
                "audio": full_audio,
                "model": model
            }
    
    def get_conversation(
        self, 
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get conversation details.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation details
        """
        endpoint = f"{self.base_url}/{self.version}/conversations/{conversation_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            self._handle_error_response(response)
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Get conversation request failed: {e}")
            raise
    
    def list_conversations(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List conversations.
        
        Args:
            limit: Maximum number of conversations to return
            offset: Pagination offset
            
        Returns:
            List of conversations
        """
        endpoint = f"{self.base_url}/{self.version}/conversations"
        
        try:
            response = requests.get(
                endpoint,
                headers=self._get_headers(),
                params={"limit": limit, "offset": offset},
                timeout=self.timeout
            )
            
            self._handle_error_response(response)
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"List conversations request failed: {e}")
            raise
    
    def delete_conversation(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Deletion confirmation
        """
        endpoint = f"{self.base_url}/{self.version}/conversations/{conversation_id}"
        
        try:
            response = requests.delete(
                endpoint,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            self._handle_error_response(response)
            
            # Remove from local cache
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
                
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Delete conversation request failed: {e}")
            raise
    
    def submit_feedback(
        self,
        conversation_id: str,
        message_id: str,
        feedback_type: str,
        feedback_value: Union[int, float],
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback for a message.
        
        Args:
            conversation_id: Conversation ID
            message_id: Message ID
            feedback_type: Type of feedback (thumbs_up, thumbs_down, rating, report)
            feedback_value: Numeric feedback value
            comment: Optional comment
            
        Returns:
            Feedback submission confirmation
        """
        endpoint = f"{self.base_url}/{self.version}/feedback"
        
        payload = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "feedback_type": feedback_type,
            "feedback_value": feedback_value
        }
        
        if comment:
            payload["comment"] = comment
            
        try:
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            self._handle_error_response(response)
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Submit feedback request failed: {e}")
            raise
    
    def search(
        self,
        query: str,
        search_type: str = "conversations",
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search conversations or messages.
        
        Args:
            query: Search query
            search_type: Type of search (conversations, messages)
            limit: Maximum number of results to return
            offset: Pagination offset
            
        Returns:
            Search results
        """
        endpoint = f"{self.base_url}/{self.version}/search/{search_type}"
        
        payload = {
            "query": query,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            self._handle_error_response(response)
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Search request failed: {e}")
            raise
    
    def speech_to_text(
        self,
        audio_source: Union[str, bytes],
        language: Optional[str] = None,
        provider: str = "openai"
    ) -> Dict[str, Any]:
        """
        Convert speech to text.
        
        Args:
            audio_source: Path to audio file or audio bytes
            language: Optional language code
            provider: Speech-to-text provider
            
        Returns:
            Transcription result
        """
        endpoint = f"{self.base_url}/{self.version}/speech-to-text"
        
        # Read audio file if a path was provided
        if isinstance(audio_source, str):
            with open(audio_source, 'rb') as f:
                audio_data = f.read()
        else:
            audio_data = audio_source
        
        files = {
            'file': ('audio.webm', audio_data)
        }
        
        data = {
            'provider': provider
        }
        
        if language:
            data['language'] = language
        
        try:
            response = requests.post(
                endpoint,
                headers={h: v for h, v in self._get_headers().items() if h != "Content-Type"},
                data=data,
                files=files,
                timeout=self.timeout
            )
            
            self._handle_error_response(response)
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Speech-to-text request failed: {e}")
            raise