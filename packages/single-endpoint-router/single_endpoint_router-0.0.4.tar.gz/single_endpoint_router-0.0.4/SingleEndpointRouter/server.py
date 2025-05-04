from __future__ import annotations

import json
import os
import sqlite3
from typing import Iterable, Sequence

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response
import yaml

__all__: list[str] = ["Server"]


class Server:
    """
    Single‑endpoint Router.

    Examples
    --------
    >>> from SingleEndpointRouter import Server
    >>> endpoints = ["http://10.0.0.1:3000", "http://10.0.0.2:3100"]
    >>> app = Server(endpoints, "config.yaml")
    >>> app.run(debug=True, host="0.0.0.0", port=8000)
    """

    # ------------------------------- constructor ------------------------------- #
    def __init__(
        self, endpoints_or_conf: Sequence[str] | str, conf_path: str | None = None
    ):
        # endpoints_or_conf can be either a list of endpoints or simply a path to
        # config.yaml when endpoints are not supplied.
        if isinstance(endpoints_or_conf, (str, os.PathLike)) and conf_path is None:
            self._endpoints: list[str] = []
            self._conf_path = str(endpoints_or_conf)
        else:
            self._endpoints = list(endpoints_or_conf)  # type: ignore[arg-type]
            self._conf_path = conf_path or "config.yaml"

        self.app = FastAPI()

        # ------------ configuration ------------- #
        self._path_to_servers: dict[str, list[str]] = {}
        self._server_endpoint_payloads: dict[str, dict[str, list[dict]]] = {}
        self._read_config(self._conf_path)

        # ------------ sqlite cache -------------- #
        self._db_path = os.path.join(os.path.dirname(__file__), "cache.db")
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._cursor = self._conn.cursor()
        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS endpoint_cache ("
            "method TEXT, path TEXT, payload_keys TEXT, server TEXT, "
            "PRIMARY KEY(method, path, payload_keys))"
        )
        self._conn.commit()

        # ------------ fastapi route ------------- #
        self.app.api_route(
            "/{path:path}",
            methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        )(self._proxy)

    # ------------------------------ public api ------------------------------ #
    def run(self, *, debug: bool = True, host: str = "127.0.0.1", port: int = 8000):
        """
        Start the router using uvicorn.

        Parameters
        ----------

        debug : bool
            If True, run with log_level="debug".  Auto‑reload is disabled to avoid
            uvicorn's *application import string* warning.
        """
        print(f"* Running on http://{host}:{port} (Press CTRL+C to quit)")
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="debug" if debug else "warning",
            #  reload=debug,  # removed: requires import string
        )

    # --------------------------- internal helpers --------------------------- #
    def _read_config(self, path: str):
        if not os.path.isfile(path):
            return
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        if not cfg:
            return
        # Support YAML structure where top-level keys are server URLs
        # {
        #   "http://127.0.0.1:3000": {
        #     cache_timeout: ...,
        #     endpoints: {
        #       "/get_log_files": { payload: [...] },
        #       ...
        #     }
        #   },
        #   ...
        # }
        self._server_endpoint_payloads = {}
        self._endpoints = []
        for server_url, server_conf in cfg.items():
            self._endpoints.append(server_url)
            endpoints = server_conf.get("endpoints", {})
            self._server_endpoint_payloads[server_url] = {}
            for endpoint_path, endpoint_conf in endpoints.items():
                payloads = endpoint_conf.get("payload", [])
                self._server_endpoint_payloads[server_url][endpoint_path] = payloads

    # ------------------------- sqlite cache helpers ------------------------- #
    def _get_cached_server(self, method: str, path: str, payload_keys: Iterable[str]):
        pk = ",".join(payload_keys)
        self._cursor.execute(
            "SELECT server FROM endpoint_cache WHERE method=? AND path=? AND payload_keys=?",
            (method, path, pk),
        )
        row = self._cursor.fetchone()
        return row[0] if row else None

    def _set_cached_server(
        self, method: str, path: str, payload_keys: Iterable[str], server: str
    ):
        pk = ",".join(payload_keys)
        self._cursor.execute(
            "REPLACE INTO endpoint_cache (method, path, payload_keys, server) VALUES (?, ?, ?, ?)",
            (method, path, pk, server),
        )
        self._conn.commit()

    # -------------------------- request forwarding -------------------------- #
    async def _send_request(
        self,
        server: str,
        method: str,
        path: str,
        request: Request,
        body: bytes | None,
    ):
        url = server + path
        headers = dict(request.headers)
        headers.pop("host", None)
        params = dict(request.query_params)

        async with httpx.AsyncClient() as client:
            rsp = await client.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                content=body if method in {"POST", "PUT", "PATCH"} else None,
            )
        return rsp

    # ------------------------------ proxy route ----------------------------- #
    async def _proxy(self, request: Request, path: str):
        method = request.method
        p = "/" + path

        body = await request.body() if method in {"POST", "PUT", "PATCH"} else None

        # payload keys and values for matching
        if method == "POST":
            try:
                json_body = json.loads(body.decode()) if body else {}
                payload_keys = tuple(sorted(json_body.keys()))
            except Exception:  # noqa: BLE001
                json_body = {}
                payload_keys = ()
        else:
            json_body = {}
            payload_keys = ()

        # ----------- 1. Try to match endpoint+payload in config -----------
        matched_server = None
        for server, endpoints in self._server_endpoint_payloads.items():
            if p in endpoints:
                payload_list = endpoints[p]
                # If no payloads defined, treat as match for any payload
                if not payload_list:
                    matched_server = server
                    break
                for payload in payload_list:
                    # All keys in payload must match and values must match
                    if all(json_body.get(k) == v for k, v in payload.items()):
                        matched_server = server
                        break
                if matched_server:
                    break

        if matched_server:
            rsp = await self._send_request(matched_server, method, p, request, body)
            return Response(
                content=rsp.content,
                status_code=rsp.status_code,
                headers=dict(rsp.headers),
            )

        # ---------- 2. cache lookup ----------
        cached_server = self._get_cached_server(method, p, payload_keys)
        if cached_server:
            rsp = await self._send_request(cached_server, method, p, request, body)
            return Response(
                content=rsp.content,
                status_code=rsp.status_code,
                headers=dict(rsp.headers),
            )

        # ---------- 3. fallback: try all servers ----------
        tried = []
        # Try all servers from config first
        for server in self._endpoints:
            if server not in tried:
                rsp = await self._send_request(server, method, p, request, body)
                if rsp.status_code == 200:
                    self._set_cached_server(method, p, payload_keys, server)
                    return Response(
                        content=rsp.content,
                        status_code=rsp.status_code,
                        headers=dict(rsp.headers),
                    )
                tried.append(server)

        return Response(status_code=404)
