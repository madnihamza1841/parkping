from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and not isinstance(response.data, dict):
        response.data = {'detail': str(response.data)}
    elif response is not None and 'detail' not in response.data:
        errors = []
        for field, messages in response.data.items():
            if isinstance(messages, list):
                for msg in messages:
                    errors.append(f'{field}: {msg}')
            else:
                errors.append(f'{field}: {messages}')
        response.data = {'detail': ' | '.join(errors)}
    return response
