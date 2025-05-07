"""
Pipeline controller for the Zeebee AI Python SDK.
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
import websockets
from .exceptions import PipelineException

class PipelineController:
    """Controller for pipeline operations."""
    
    def __init__(self, client):
        """
        Initialize the pipeline controller.
        
        Args:
            client: ZeebeeClient instance
        """
        self.client = client
        
    def create_pipeline(
        self,
        name: str,
        stages: List[Dict[str, Any]],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new pipeline.
        
        Args:
            name: Pipeline name
            stages: Pipeline stages
            description: Optional pipeline description
            
        Returns:
            Created pipeline details
        """
        endpoint = f"{self.client.base_url}/{self.client.version}/pipelines"
        
        payload = {
            "name": name,
            "stages": stages
        }
        
        if description:
            payload["description"] = description
            
        try:
            response = self.client._session.post(
                endpoint,
                headers=self.client._get_headers(),
                json=payload,
                timeout=self.client.timeout
            )
            
            self.client._handle_error_response(response)
            return response.json()
            
        except Exception as e:
            raise PipelineException(f"Failed to create pipeline: {e}")
    
    def execute_pipeline(
        self,
        pipeline_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            input_data: Input data for the pipeline
            
        Returns:
            Execution details
        """
        endpoint = f"{self.client.base_url}/{self.client.version}/pipelines/{pipeline_id}/execute"
        
        try:
            response = self.client._session.post(
                endpoint,
                headers=self.client._get_headers(),
                json=input_data,
                timeout=self.client.timeout
            )
            
            self.client._handle_error_response(response)
            return response.json()
            
        except Exception as e:
            raise PipelineException(f"Failed to execute pipeline: {e}")
    
    async def listen_to_execution(self, execution_id: str):
        """
        Listen to pipeline execution updates.
        
        Args:
            execution_id: Execution ID
            
        Yields:
            Execution updates
        """
        ws_url = f"{self.client.base_url.replace('http', 'ws')}/{self.client.version}/pipelines/executions/{execution_id}/stream"
        
        try:
            async with websockets.connect(ws_url, extra_headers=self.client._get_headers()) as ws:
                while True:
                    message = await ws.recv()
                    
                    try:
                        data = json.loads(message)
                        yield data
                        
                        # Break if execution is complete
                        if data.get("is_complete", False):
                            break
                            
                    except json.JSONDecodeError:
                        raise PipelineException(f"Invalid JSON from execution stream: {message}")
                        
        except Exception as e:
            raise PipelineException(f"Failed to listen to execution: {e}")
