class InvalidAPIToken(Exception):
    def __init__(self, token):
        super().__init__(f"Invalid API token was provided: {token}")


class ResponseError(Exception):
    def __init__(self, response: dict, verbose: bool = False) -> None:
        message = (
            "Cannot parse response from server. "
            "If you are sure that the response is correct, "
            "than please report this as a bug. "
        )
        if verbose:
            message += f"Response: {response}"

        super().__init__(message)
