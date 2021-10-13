from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from dataclasses import asdict
from typing import Any, Callable, Dict

@lambda_handler_decorator
def lambda_dataclass_response(handler: Callable[..., Any], event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    response = handler(event, context)
    return asdict(response)