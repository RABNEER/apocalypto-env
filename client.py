from openenv.core.env_client import EnvClient
from .models import ApocalyptoAction, ApocalyptoObservation, ApocalyptoState
from typing import Type

class ApocalyptoClient(EnvClient):
    """
    Standard OpenEnv client. 
    By subclassing EnvClient, users can connect to our HuggingFace Space seamlessly using websockets.
    """
    
    @property
    def action_type(self) -> Type[ApocalyptoAction]:
        return ApocalyptoAction
        
    @property
    def observation_type(self) -> Type[ApocalyptoObservation]:
        return ApocalyptoObservation
        
    @property
    def state_type(self) -> Type[ApocalyptoState]:
        return ApocalyptoState
