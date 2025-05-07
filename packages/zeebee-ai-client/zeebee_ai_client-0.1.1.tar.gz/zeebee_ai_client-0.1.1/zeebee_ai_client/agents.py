"""
Agent controller for the Zeebee AI Python SDK.
"""

from typing import Dict, List, Any, Optional
from .exceptions import AgentException

class AgentController:
    """Controller for agent operations."""
    
    def __init__(self, client):
        """
        Initialize the agent controller.
        
        Args:
            client: ZeebeeClient instance
        """
        self.client = client
        
    def create_agent(
        self,
        name: str,
        type: str,
        config: Dict[str, Any],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new agent.
        
        Args:
            name: Agent name
            type: Agent type
            config: Agent configuration
            description: Optional agent description
            
        Returns:
            Created agent details
        """
        endpoint = f"{self.client.base_url}/{self.client.version}/agents"
        
        payload = {
            "name": name,
            "type": type,
            "config": config
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
            raise AgentException(f"Failed to create agent: {e}")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent details.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent details
        """
        endpoint = f"{self.client.base_url}/{self.client.version}/agents/{agent_id}"
        
        try:
            response = self.client._session.get(
                endpoint,
                headers=self.client._get_headers(),
                timeout=self.client.timeout
            )
            
            self.client._handle_error_response(response)
            return response.json()
            
        except Exception as e:
            raise AgentException(f"Failed to get agent: {e}")
    
    def update_agent(
        self,
        agent_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            update_data: Data to update
            
        Returns:
            Updated agent details
        """
        endpoint = f"{self.client.base_url}/{self.client.version}/agents/{agent_id}"
        
        try:
            response = self.client._session.patch(
                endpoint,
                headers=self.client._get_headers(),
                json=update_data,
                timeout=self.client.timeout
            )
            
            self.client._handle_error_response(response)
            return response.json()
            
        except Exception as e:
            raise AgentException(f"Failed to update agent: {e}")
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Deletion confirmation
        """
        endpoint = f"{self.client.base_url}/{self.client.version}/agents/{agent_id}"
        
        try:
            response = self.client._session.delete(
                endpoint,
                headers=self.client._get_headers(),
                timeout=self.client.timeout
            )
            
            self.client._handle_error_response(response)
            return response.json()
            
        except Exception as e:
            raise AgentException(f"Failed to delete agent: {e}")
