from app.shared.exceptions.base_exception import (
    ApplicationException
)


class NotFoundException(ApplicationException):

    def __init__(

        self,

        message: str

    ):

        super().__init__(

            message=message,

            status_code=404
        )