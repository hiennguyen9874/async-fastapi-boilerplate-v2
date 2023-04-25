__all__ = ["ErrException"]


class ErrException(Exception):
    __slots__ = ("status_code", "status_text", "msg")

    def __init__(self, status_code: int, status_text: str, msg: str):
        self.status_code = status_code
        self.status_text = status_text
        self.msg = msg


class ErrBadRequest(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, status_text="bad_request", msg=msg)


class ErrNotFound(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=404, status_text="not_found", msg=msg)


class ErrUnauthorized(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=401, status_text="unauthorized", msg=msg)


class ErrInternalServerError(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=500, status_text="internal_server_error", msg=msg)


class ErrRequestTimeoutError(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=408, status_text="request_timeout", msg=msg)


class ErrInvalidJWTToken(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=401, status_text="invalid_jwt_token", msg=msg)


class ErrInvalidJWTClaims(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=401, status_text="invalid_jwt_claims", msg=msg)


class ErrValidation(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=422, status_text="validation", msg=msg)


class ErrWrongPassword(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=401, status_text="wrong_password", msg=msg)


class ErrTokenNotFound(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=401, status_text="token_not_found", msg=msg)


class ErrInactiveUser(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=403, status_text="inactive_user", msg=msg)


class ErrNotEnoughPrivileges(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=403, status_text="not_enough_privileges", msg=msg)


class ErrNotFoundRefreshTokenRedis(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=401, status_text="not_found_refresh_token", msg=msg)


class ErrUserAlreadyVerified(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, status_text="user_already_verified", msg=msg)


class ErrUserNotVerified(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, status_text="user_not_verified", msg=msg)


class ErrMakeRequest(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, status_text="make_request_error", msg=msg)


class ErrCallRequest(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, status_text="call_request_error", msg=msg)


class ErrReadBodyRequest(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, status_text="read_body_request_error", msg=msg)


class ErrExistsEmail(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, status_text="email_exists", msg=msg)


class ErrApiDisable(ErrException):
    def __init__(self, msg: str):
        super().__init__(status_code=403, status_text="api_disable", msg=msg)
