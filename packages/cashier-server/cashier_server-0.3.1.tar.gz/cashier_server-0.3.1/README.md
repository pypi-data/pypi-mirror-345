# cashier-server-python
Cashier synchronization server, in Python

Ledger-cli REST server for [Cashier](https://github.com/alensiljak/cashier) PWA, implemented in Python with FastAPI.

Cashier Server acts as a mediator between Cashier PWA and Ledger CLI, forwarding queries to Ledger and the results to Cashier. Used for synchronizing the ledger data in Cashier.

This is a Python implementation of the Cashier Server using FastAPI.

## Installation

1. Clone the repository
2. Install `uv`

## Run

Make sure that Ledger CLI is configured and can be called from the current directory.
Then run:

```sh
run.cmd
# or
uv run python app.py
# Or uvicorn directly:
uvicorn app:app --host 0.0.0.0 --port 3000
```

## API Endpoints

- `/` - Execute a ledger command
- `/hello` - Return a base64-encoded image
- `/ping` - Simple ping endpoint
- `/shutdown` - Request server shutdown (not fully implemented)

## Development

VSCode recommended.
Run the `run.cmd` script to start the server.
Or run from VSCode to debug.


```markdown:CHANGELOG.md
# Changelog

Notable application changes.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2023-09-15

### Added

- Initial Python implementation with FastAPI
- Endpoints: /, /hello, /ping, /shutdown
- CORS support
- Basic logging
```

## Notes on the Implementation

1. The Python implementation maintains the same endpoints as the Rust version:
   - `/` - For executing ledger commands
   - `/hello` - For returning a base64-encoded image
   - `/ping` - Simple health check
   - `/shutdown` - For shutdown requests

2. CORS is enabled for all origins, similar to the Rust implementation.

3. Logging is configured to output to the console.

4. The server runs on 0.0.0.0:3000, matching the Rust implementation.

5. For the `/hello` endpoint, you would need to provide an actual image file named "hello.png" in the same directory as the app.py file.
