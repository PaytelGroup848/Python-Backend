from fastapi import APIRouter

from app.shared.metrics.metrics_service import (
    metrics_service
)
from app.shared.metrics.queue_metrics_service import (
    queue_metrics_service
)

router = APIRouter()


@router.get("/metrics")
async def get_metrics():

    metrics = await (
        metrics_service.get_metrics()
    )

    queue_metrics = await (
        queue_metrics_service
        .get_queue_metrics()
    )

    return {

        **metrics,

        **queue_metrics,
    }