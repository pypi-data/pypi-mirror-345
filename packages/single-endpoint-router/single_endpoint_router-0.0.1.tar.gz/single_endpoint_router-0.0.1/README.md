# SingleEndpointRouter

**SingleEndpointRouter** is a lightweight, FastAPI-based reverse proxy and router that forwards each incoming request to the first backend server that responds with **200 OK**. It supports advanced routing based on endpoint paths and request payloads, and remembers successful routes in a SQLite cache for fast subsequent lookups.

---

## Features

- **Single endpoint**: Expose one API endpoint and route requests to multiple backend servers.
- **Payload-aware routing**: Route requests based on both endpoint path and request payload.
- **YAML configuration**: Flexible, human-readable configuration for endpoints and payloads.
- **Automatic caching**: Remembers which backend handled which request for faster future routing.
- **FastAPI & Uvicorn**: High-performance async Python stack.
- **SQLite cache**: Persistent, lightweight caching of routing decisions.

---

## Installation

Install from PyPI (after publishing):

```bash
pip install SingleEndpointRouter
```

Or install from a local wheel:

```bash
pip install SingleEndpointRouter-0.0.2-py3-none-any.whl
```

---

## Quick Start

### 1. Create a `config.yaml`

Example:

```yaml
"http://127.0.0.1:3000":
  cache_timeout: 6000
  endpoints:
    "/get_log_files":
      payload:
        - name: "log_file.log"
          path: "c:/logs"
        - name: "backup_log.log"
          path: "d:/backup/logs"
    "/load_log_file":
      payload:
        - name: "log_file.log"
          path: "c:/logs"

"http://127.0.0.1:3100":
  cache_timeout: 5000
  endpoints:
    "/archive_logs":
      payload:
        - source: "c:/logs"
          destination: "e:/archives"
          compress: true
```

### 2. Start the router

```python
from SingleEndpointRouter import Server

# Option 1: Use only the config file
app = Server("config.yaml")

# Option 2: Provide fallback endpoints and config file
endpoints = [
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3100",
    "http://127.0.0.1:3200",
]
app = Server(endpoints, "config.yaml")

app.run(debug=True, host="0.0.0.0", port=8000)
```

Console output:

```
* Running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## How It Works

1. **Routing by Path and Payload**:  
   When a request is received, the router checks the YAML config for a matching backend server based on the request path and payload (for POST/PUT/PATCH). If a match is found, the request is forwarded to that server.

2. **Fallback and Caching**:  
   If no match is found, the router checks its cache for a previously successful backend for this method/path/payload combination. If still not found, it tries all configured endpoints in order until one responds with 200 OK, then caches that choice.

3. **Payload Matching**:  
   For endpoints with a `payload` list, the request payload must match one of the payload dictionaries exactly (all keys and values must match).

---

## Configuration File (`config.yaml`)

The configuration file is a YAML file where each top-level key is a backend server URL. Each server can define:

- `cache_timeout`: (optional) Not currently used, for future cache expiry support.
- `endpoints`: A mapping of endpoint paths to payload matchers.

Example:

```yaml
"http://127.0.0.1:3000":
  cache_timeout: 6000
  endpoints:
    "/get_log_files":
      payload:
        - name: "log_file.log"
          path: "c:/logs"
        - name: "backup_log.log"
          path: "d:/backup/logs"
    "/load_log_file":
      payload:
        - name: "log_file.log"
          path: "c:/logs"
```

**Routing logic:**

- If a request matches both the endpoint path and one of the payloads, it is routed to that server.
- If no payload matches, the router tries all servers in order as fallback.

---

## API

### `class Server(endpoints_or_conf, conf_path="config.yaml")`

| Parameter             | Type                     | Description                                           |
| --------------------- | ------------------------ | ----------------------------------------------------- |
| `endpoints_or_conf`   | `Sequence[str] \| str`   | List of fallback backend URLs **or** path to config file |
| `conf_path`           | `str` (optional)         | Path to config file when first argument is a list     |

#### Methods

- `run(debug=True, host="127.0.0.1", port=8000)`  
  Starts the FastAPI/Uvicorn server.

---

## Example Request

Suppose your config contains:

```yaml
"http://127.0.0.1:3000":
  endpoints:
    "/get_log_files":
      payload:
        - name: "log_file.log"
          path: "c:/logs"
"http://127.0.0.1:3100":
  endpoints:
    "/get_log_files":
      payload:
        - name: "backup_log.log"
          path: "d:/backup/logs"
```

A POST to `http://127.0.0.1:8000/get_log_files` with payload:

```json
{"name": "backup_log.log", "path": "d:/backup/logs"}
```

will be routed to `http://127.0.0.1:3100/get_log_files`.

---

## Advanced Usage

- **Fallback**: If no config match is found, the router tries all endpoints in order.
- **Caching**: Once a backend is found for a method/path/payload, it is cached for future requests.
- **Stateless**: The router does not modify request or response bodies.

---

## License

MIT

---

## Project Links

- [GitHub Repository](https://github.com/dsharathrao/SingleEndpointRouter)
- [PyPI Project](https://pypi.org/project/SingleEndpointRouter/)
