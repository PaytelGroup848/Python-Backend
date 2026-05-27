from fastapi import APIRouter

from prometheus_client import (
    generate_latest
)

from fastapi.responses import (
    Response
)

router = APIRouter()


@router.get("/prometheus")
async def prometheus_metrics():

    return Response(

        content=generate_latest(),

        media_type="text/plain"
    )