"""
Rate limiting middleware for APIs

This module provides functionality to check if a request should be rate limited
by communicating with the RateLimit API service.
"""

import json
import requests
from typing import Dict, Any, Optional, Tuple, Union


def is_rate_limited(request, api_token: str) -> Optional[Tuple[Dict[str, Any], int, Dict[str, str]]]:
    """
    Checks if a request should be rate limited based on RateLimit API
    
    This function evaluates if a request should be rate limited by communicating with the
    RateLimit API service. It validates the API token, extracts request information, and
    sends it to the rate limiting service for evaluation.
    
    Args:
        request: The request object to check for rate limiting. Should have method, url and headers attributes.
        api_token: The API token for authenticating with the RateLimit API (must start with "rlimit_")
    
    Returns:
        If rate limited or error: A tuple of (response_body, status_code, headers)
        If not rate limited: None
    
    Example:
        ```python
        from ratelimitapi import is_rate_limited
        
        def handle_request(request):
            limited_response = is_rate_limited(request, "rlimit_your_token_here")
            if limited_response:
                response_body, status_code, headers = limited_response
                # Return the rate limit response to the client
                return create_response(response_body, status_code, headers)
                
            # Continue with normal request processing
            # ...
        ```
    """
    # Validate API token
    if not api_token.startswith('rlimit_'):
        return create_error_response({
            'error': 'invalid_api_token', 
            'message': 'API token must start with "rlimit_"'
        }, 401)
    
    # Extract request information
    method = request.method
    url = request.url
    headers = {}
    
    # Handle different request object implementations
    # For Flask/Werkzeug style
    if hasattr(request, 'headers') and hasattr(request.headers, 'items'):
        headers = {key: value for key, value in request.headers.items()}
    # For Django style
    elif hasattr(request, 'headers') and callable(getattr(request.headers, 'get', None)):
        headers = {key: request.headers.get(key) for key in request.headers}
    # For standard dict style
    elif isinstance(request.headers, dict):
        headers = request.headers
    
    # Call rate limit API
    try:
        rl_res = requests.post(
            'https://api.ratelimitapi.com/v1/limit',
            headers={
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            },
            json={'method': method, 'url': url, 'headers': headers}
        )
        
        # Handle rate limited response
        if rl_res.status_code == 429:
            return rl_res.json(), 429, dict(rl_res.headers)
        
        # Handle error responses
        if not rl_res.ok:
            try:
                error_data = rl_res.json()
                if not error_data.get('success', True) and error_data.get('error'):
                    status = 403 if error_data.get('error') == 'forbidden_url' else 400
                    return create_error_response(error_data, status)
            except ValueError:
                return {'message': rl_res.text}, rl_res.status_code, {'Content-Type': 'text/plain'}
                
        return None
        
    except requests.RequestException as e:
        return create_error_response({
            'error': 'api_connection_error',
            'message': f'Failed to connect to RateLimit API: {str(e)}'
        }, 500)


def create_error_response(error_data: Dict[str, Any], status: int) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
    """
    Creates a standardized error response with JSON content.
    
    Args:
        error_data: Additional error information to be included in the response body
        status: HTTP status code for the response
        
    Returns:
        A tuple of (response_body, status_code, headers)
    """
    response_body = {'success': False}
    response_body.update(error_data)
    
    return response_body, status, {'Content-Type': 'application/json'}
