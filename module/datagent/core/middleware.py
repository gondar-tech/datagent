from typing import Callable, Awaitable, Any, Dict
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class Middleware(ABC):
    @abstractmethod
    async def process_request(self, context: Dict[str, Any], next_call: Callable[[], Awaitable[Any]]) -> Any:
        pass

class MiddlewarePipeline:
    def __init__(self):
        self._middlewares = []

    def add(self, middleware: Middleware):
        self._middlewares.append(middleware)

    async def execute(self, context: Dict[str, Any], target: Callable[[], Awaitable[Any]]) -> Any:
        async def _dispatch(index: int):
            if index == len(self._middlewares):
                return await target()
            
            middleware = self._middlewares[index]
            return await middleware.process_request(context, lambda: _dispatch(index + 1))

        return await _dispatch(0)

class LoggingMiddleware(Middleware):
    async def process_request(self, context: Dict[str, Any], next_call: Callable[[], Awaitable[Any]]) -> Any:
        logger.info(f"Starting request with context keys: {list(context.keys())}")
        try:
            result = await next_call()
            logger.info("Request completed successfully")
            return result
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
