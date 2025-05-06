"""
Functions generator for OpenAPI endpoints.

This module provides functions to generate Python callables for all endpoints in an OpenAPI spec.
It converts OpenAPI endpoint definitions into callable Python functions that handle parameter
validation, request formatting, and response processing.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Union
from urllib.parse import urljoin

from pydantic import BaseModel, Field, create_model
import requests

from .endpoint import list_endpoints
from .loader import to_snake

def _build_function(
    base_url: str,
    path: str,
    method: str,
    query_params: dict,
    path_params: dict,
    body_params: dict,
    func_name: str,
    doc: str,
) -> dict:
    """
    Build a callable function for an OpenAPI endpoint.
    
    Args:
        base_url: The base URL for the API.
        path: The endpoint path, may contain path parameters.
        method: The HTTP method (GET, POST, PUT, DELETE, etc.).
        query_params: Dictionary of query parameters and their schemas.
        path_params: Dictionary of path parameters and their schemas.
        body_params: Dictionary of body parameters and their schemas.
        func_name: Name to assign to the generated function.
        doc: Documentation string for the function.
        
    Returns:
        A dictionary containing the callable function and the Pydantic model for parameter validation.
    """
    # Create a dynamic Pydantic model for parameter validation
    fields = {}
    
    # Add path parameters to the model
    for param in path_params:
        fields[param] = (str, ...)  # Path params are required
        
    # Add query parameters to the model
    for param, schema in query_params.items():
        # Query params are optional by default
        fields[param] = (schema.get('type', Any), None)
        
    # Add body parameters if they exist
    has_body = len(body_params.keys()) > 0
    if has_body:
        # If body is directly passed, it should be validated separately
        # Otherwise, include body params in the model
        for param, schema in body_params.items():
            required = schema.get('required', False)
            param_type = schema.get('type', Any)
            fields[param] = (param_type, ... if required else None)
    
    # Create the model for parameter validation
    EndpointParams = create_model('EndpointParams', **fields)
   
    def _endpoint_function(*, base_url: str = base_url, **kwargs):
        """
        A function built for an OpenAPI endpoint.

        The function takes arbitrary keyword arguments, and passes on any matching
        query parameters or path parameters to the request. If a body parameter is
        present and the endpoint allows a body, the body is passed as JSON.

        The function returns the response JSON, after raising an exception if the
        request was not successful.
        """
        try:
            # Use the model created in _build_function to validate input
            validated_params = EndpointParams(**kwargs).dict(exclude_none=True)
        except Exception as e:
            return {"error": True, "message": str(e)}
        
        # Extract parameters for the request
        base = base_url
        if not base.endswith("/"):
            base += "/"
        
        # Extract path parameters for URL formatting
        path_param_values = {k: validated_params.pop(k) for k in path_params}
        url = urljoin(base, path.format(**path_param_values))
        
        # Extract query parameters
        params = {k: validated_params.pop(k) for k in query_params if k in validated_params} or None
        
        # Handle body
        if has_body:
            # If body was directly provided in kwargs, use it
            body = kwargs.get('body')
            # Otherwise, construct body from remaining validated parameters
            if body is None and body_params:
                body = {k: validated_params.get(k) for k in body_params if k in validated_params} or None
        else:
            body = None
        
        try:
            response = requests.request(method, url, params=params, json=body, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": True, "message": str(e)}

    _endpoint_function.__name__ = func_name
    _endpoint_function.__doc__ = doc or ""
    return {
        "func": _endpoint_function,
        "model": EndpointParams,
    }


def generate_tools(
    spec_src: str | Path,
    removeprefix: str | None = None,
) -> dict:
    """
    Generate callable tools from an OpenAPI specification.
    
    This function parses an OpenAPI specification and creates callable functions
    for each endpoint. The functions are attached to a SimpleNamespace object
    and returned.
    
    Args:
        spec_src: Path or URL to the OpenAPI specification file.
        removeprefix: Optional prefix to remove from endpoint paths when generating function names.
        
    Returns:
        A dict object containing callable functions for each endpoint.
    """

    functions = {}
    endpoints = list_endpoints(spec_src)
    base_url = str(spec_src).removesuffix("/openapi.json")

    for endpoint in endpoints:

        func_method = endpoint['method'].lower()
        if func_method == "post":
            func_method = "create"
        elif func_method == "put":
            func_method = "update"
        elif func_method == "delete":
            func_method = "delete"

        func_name = func_method + "_" + to_snake(endpoint['path'], removeprefix)
        func = _build_function(
            base_url=base_url,
            path=endpoint['path'],
            method=endpoint['method'],
            query_params=endpoint['params']['query_params'],
            path_params=endpoint['params']['path_params'],
            body_params=endpoint['params']['body_params'],
            func_name=func_name,
            doc=endpoint['description'],
        )
        functions[func_name] = {
            "name": func_name,
            "description": endpoint['description'],
            "func": func["func"],
            "model": func["model"],
        }

    return functions
