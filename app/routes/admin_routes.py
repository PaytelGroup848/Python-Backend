import logging

from fastapi import (
    APIRouter,
    Depends
)

from app.core.security import (
    require_role,
    require_permission
)

from app.services.audit_service import (
    log_action
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =========================
# Admin Route
# =========================

@router.get("/admin")
async def admin_only(

    user=Depends(
        require_role("admin")
    )
):

    try:

        log_action(

            user["user_id"],

            "admin_access",

            "/admin"
        )

    except Exception as e:

        logger.error(
            f"Audit log failed: {e}"
        )

    return {
        "message":
        "Admin access granted"
    }


# =========================
# Manager Route
# =========================

@router.get("/manager")
async def manager_only(

    user=Depends(
        require_role("manager")
    )
):

    try:

        log_action(

            user["user_id"],

            "manager_access",

            "/manager"
        )

    except Exception as e:

        logger.error(
            f"Audit log failed: {e}"
        )

    return {
        "message":
        "Manager access granted"
    }


# =========================
# Admin Dashboard
# =========================

@router.get("/admin-dashboard")
async def admin_dashboard(

    user=Depends(
        require_permission(
            "view_admin_dashboard"
        )
    )
):

    try:

        log_action(

            user["user_id"],

            "view_admin_dashboard",

            "/admin-dashboard"
        )

    except Exception as e:

        logger.error(
            f"Audit log failed: {e}"
        )

    return {
        "message":
        "Admin dashboard"
    }


# =========================
# Reports Route
# =========================

@router.get("/reports")
async def reports(

    user=Depends(
        require_permission(
            "view_reports"
        )
    )
):

    try:

        log_action(

            user["user_id"],

            "view_reports",

            "/reports"
        )

    except Exception as e:

        logger.error(
            f"Audit log failed: {e}"
        )

    return {
        "message":
        "Reports data"
    }