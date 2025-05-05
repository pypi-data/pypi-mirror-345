from langchain_core.exceptions import LangChainException, OutputParserException

APIStatusErrors = [LangChainException, OutputParserException]

try:
    from openai._exceptions import (
        AuthenticationError,
        ConflictError,
        InternalServerError,
        NotFoundError,
        PermissionDeniedError,
        RateLimitError,
        UnprocessableEntityError,
    )

    APIStatusErrors.extend(
        [
            AuthenticationError,
            PermissionDeniedError,
            NotFoundError,
            ConflictError,
            UnprocessableEntityError,
            RateLimitError,
            InternalServerError,
        ]
    )
except ImportError:
    pass


try:
    from anthropic._exceptions import (
        APIConnectionError,
        APIResponseValidationError,
        APIStatusError,
    )

    APIStatusErrors.extend([APIResponseValidationError, APIStatusError, APIConnectionError])
except ImportError:
    pass
