import aiohttp
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode

class APIClient:
    BINANCE_TESTNET_BASE_URL = "https://mcp-gateway-759711950494.asia-southeast1.run.app/binance_testnet"
    
    def __init__(self, axgrad_key: str):
        self.axgrad_key = axgrad_key
        self.base_url = self.BINANCE_TESTNET_BASE_URL

    def _get_signature(self, params: Dict[str, Any]) -> str:
        """(Deprecated) Signature generation is no longer used."""
        return ""
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        security_type: str = "NONE"
    ) -> Dict[str, Any]:
        """Make an HTTP request to the exchange API, sending all parameters directly including security_type and axgrad_key."""
        if params is None:
            params = {}
        # Always include security_type in the parameters
        params['security_type'] = security_type
        # Always include axgrad_key in the parameters
        params['axgrad_key'] = self.axgrad_key
        headers = {}
        url = f"{self.base_url}{endpoint}"
        request_params = None
        json_body = None

        if method == 'GET':
            request_params = params
            json_body = None
        else:
            request_params = None
            json_body = params

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, params=request_params, json=json_body) as response:
                return await response.json()
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, security_type: str = "NONE") -> Dict[str, Any]:
        """Make a GET request to the exchange API with security type."""
        return await self._request('GET', endpoint, params, security_type)
    
    async def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None, security_type: str = "TRADE") -> Dict[str, Any]:
        """Make a POST request to the exchange API with security type."""
        return await self._request('POST', endpoint, params, security_type)
    
    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, security_type: str = "TRADE") -> Dict[str, Any]:
        """Make a DELETE request to the exchange API with security type."""
        return await self._request('DELETE', endpoint, params, security_type) 