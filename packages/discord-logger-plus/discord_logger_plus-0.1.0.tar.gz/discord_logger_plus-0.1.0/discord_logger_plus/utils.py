import asyncio
import functools
from typing import Callable, Any, TypeVar, Awaitable
from .handlers import LogLevel

T = TypeVar('T')

def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    """에러 처리를 위한 데코레이터"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            self = args[0]
            self.logger.error(f"{func.__name__} 실패: {str(e)}")
            return None
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self = args[0]
            self.logger.error(f"{func.__name__} 실패: {str(e)}")
            return None
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

def get_color_for_level(level: LogLevel) -> int:
    """로그 레벨에 따른 Discord 임베드 색상 반환"""
    colors = {
        LogLevel.DEBUG: 0x808080,    # 회색
        LogLevel.INFO: 0x00FF00,     # 초록색
        LogLevel.WARNING: 0xFFFF00,  # 노란색
        LogLevel.ERROR: 0xFF0000,    # 빨간색
        LogLevel.CRITICAL: 0xFF0000  # 빨간색
    }
    return colors.get(level, 0x808080)

def format_message(message: str, **kwargs) -> str:
    """메시지 포맷팅"""
    return message.format(**kwargs)

def should_log(context: dict, filters: list) -> bool:
    """필터를 통과하는지 확인"""
    return all(filter_func(context) for filter_func in filters)

async def run_in_executor(func: Callable[..., T], *args, **kwargs) -> T:
    """함수를 executor에서 실행"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs)) 