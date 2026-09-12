import httpx


http_client = httpx.AsyncClient(

    timeout=httpx.Timeout(120.0, connect=10.0),

    limits=httpx.Limits(

        max_connections=1000,

        max_keepalive_connections=200,
    ),
)