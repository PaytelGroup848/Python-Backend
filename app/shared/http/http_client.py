import httpx


http_client = httpx.AsyncClient(

    timeout=30.0,

    limits=httpx.Limits(

        max_connections=1000,

        max_keepalive_connections=200,
    ),
)