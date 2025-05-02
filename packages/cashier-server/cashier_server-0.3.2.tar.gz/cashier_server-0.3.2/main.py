#!/usr/bin/env python3
"""
Cashier Server - Ledger-cli REST server for Cashier PWA
FastAPI implementation
"""

import base64
from json import JSONEncoder
import logging
import subprocess
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cashier-server")

app = FastAPI(
    title="Cashier Server",
    description="Ledger-cli REST server for Cashier PWA",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def ledger(command: Optional[str] = None):
    """
    Execute a ledger command and return the result.
    
    Args:
        query: The ledger command to execute
        
    Returns:
        The result of the ledger command
    """
    if not command:
        return {"error": "No query provided"}

    logger.info("Executing ledger command: %s", command)

    try:
        # Execute the ledger command
        process = subprocess.run(
            ["ledger"] + command.split(),
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )

        if process.returncode == 0:
            output = process.stdout
        else:
            output = process.stderr

        result = output.splitlines()
        return result
    except subprocess.CalledProcessError as e:
        logger.error("Error executing ledger command: %s", e)
        return {"error": str(e), "stderr": e.stderr}

@app.get("/hello")
async def hello_img():
    """
    Return a base64-encoded image.
    """
    # This is a placeholder - you would need to replace with your actual image
    with open("hello.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    return encoded_string


@app.get("/ping")
async def ping():
    """
    Simple ping endpoint to check if the server is running.
    """
    return "pong"


@app.get("/shutdown")
async def shutdown():
    """
    Shutdown the server.
    """
    logger.info("Shutdown requested")

    if hasattr(app.state, "server"):
        app.state.server.should_exit = True
        return {"message": "Server shut down"}
    else:
        return {"message": "Server not running"}


def main():
    '''
    Entry point for the executable script.
    '''
    logger.info("Starting Cashier Server on 0.0.0.0:3000")
    # Create a server instance that can be referenced
    # uvicorn.run(app, host="0.0.0.0", port=3000)
    config = uvicorn.Config(app, host="0.0.0.0", port=3000)
    server = uvicorn.Server(config)

    # Store the server instance in the app state
    app.state.server = server

    server.run()


if __name__ == "__main__":
    main()
