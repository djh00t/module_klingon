"""
handler.py

This module defines the FastAPI application that serves as the OpenFaaS function for generating unique hexadecimal serial numbers.
It includes endpoints for generating serial numbers in various formats based on the Accept header of the request.

The module uses the `klingon_serial` Python module to generate the serial numbers and defines custom response classes to handle
different content types.

It can be run standalone using Uvicorn for local development and testing purposes.
"""

from fastapi import FastAPI, Header, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from klingon_serial import generate_serial
from starlette.responses import Response
from typing import Optional
import uvicorn

import yaml

class XMLResponse(Response):
    media_type = "application/xml"

class YAMLResponse(Response):
    media_type = "application/yaml"

app = FastAPI()

@app.get("/health")
async def health():
    # Health check endpoint; returns a 200 OK response to indicate the service is up and running.
    return PlainTextResponse("OK", status_code=200)

@app.get("/favicon.ico")
async def favicon():
    # Endpoint to serve the favicon; returns a 204 No Content response as there is no favicon.
    return Response(content="", media_type="image/x-icon", status_code=204)


@app.get("/")
async def root(response_format: Optional[str] = Query(None, alias='format')):
    # Root endpoint that generates and returns a unique serial number in the requested format.
    # The Accept header determines the response content type: JSON, plain text, HTML, XML, or XHTML.
    # If the Accept header is not supported, it returns a 406 Not Acceptable with an error message.
    unique_serial = generate_serial().upper()
    data = {"serial": unique_serial}
    if response_format:
        if response_format == "json":
            return JSONResponse(content=data)
        elif response_format == "text":
            return PlainTextResponse(unique_serial)
        elif response_format == "html":
            html_content = f'<html><body><p>{unique_serial}</p></body></html>'
            return HTMLResponse(content=html_content)
        elif response_format == "xml":
            xml_content = f'<root><serial>{unique_serial}</serial></root>'
            return XMLResponse(content=xml_content)
        elif response_format == "xhtml":
            xhtml_content = f'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><title>Serial Number</title></head><body><p>{unique_serial}</p></body></html>'
            return HTMLResponse(content=xhtml_content)
        elif response_format == "yaml":
            yaml_content = yaml.dump(data)
            return YAMLResponse(content=yaml_content)
        else:
            error_data = {
                "error": "Unsupported Accept header",
                "accepted_formats": [
                    "application/json",
                    "text/plain",
                    "text/html",
                    "application/xml",
                    "text/xml",
                    "application/xhtml+xml",
                    "application/yaml"
                    "application/xhtml+xml"
                ]
            }
            return JSONResponse(content=error_data, status_code=406)
    # Default to JSON response if no Accept header is provided or if it's not recognized
    return JSONResponse(content=data)

if __name__ == "__main__":
    import pytest
    # Run the pytest suite before starting the server
    test_exit_code = pytest.main(['-v'])
    if test_exit_code != 0:
        # If tests fail, exit with the test exit code
        import sys
        sys.exit(test_exit_code)
    # If run as the main module, start the Uvicorn server to serve the FastAPI application.
    uvicorn.run("openfaas.handler:app", host="0.0.0.0", port=8000, reload=True)

