import json
from types import NoneType
from typing import Optional, Union, Annotated

from ..models import *
from ..base_model import Page, Service
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from httpx import Auth
from ..http_client import HttpClient

class Info(Service):
    
    def get_info(
        self,
    )-> InfoResponse:
        endpoint_url = "/info"
        loc = locals()
        headers = {}
        params = {}
        path_params = {}
        
        response = self.http_client.get(
            url=endpoint_url, path_params=path_params, params=params, headers=headers
        )
        
        return InfoResponse(**response.json())
    