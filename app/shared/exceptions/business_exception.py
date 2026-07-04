from app.shared.exceptions.base_exception import (
    ApplicationException
)


class BusinessException(
    ApplicationException
):
    """
    Raised when a business rule or domain constraint
    is violated during application execution.
    """

    pass
