class BaseCustomException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class NotFound(BaseCustomException):
    pass


class AlreadyExists(BaseCustomException):
    pass


class NotNullViolationError(BaseCustomException):
    pass


class ForeignKeyViolationError(BaseCustomException):
    pass
