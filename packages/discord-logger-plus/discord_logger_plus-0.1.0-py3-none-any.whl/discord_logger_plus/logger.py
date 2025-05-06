import os
import logging
import requests
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any, Callable
from enum import Enum
from functools import wraps
from dotenv import load_dotenv
from supabase import create_client, Client
from logging.handlers import RotatingFileHandler
from .handlers import LogLevel, BaseHandler, DiscordWebhookHandler, SupabaseHandler, FileHandler
from .config import LoggerConfig
from .utils import handle_errors, format_message, should_log, run_in_executor

def handle_errors(func):
    """에러 처리를 위한 데코레이터"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            self = args[0]
            self.logger.error(f"{func.__name__} 실패: {str(e)}")
            return None
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self = args[0]
            self.logger.error(f"{func.__name__} 실패: {str(e)}")
            return None
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

class DiscordLogger:
    def __init__(
        self,
        name: str,
        webhook_url: Optional[str] = None,
        webhook_levels: Optional[List[LogLevel]] = None,
        log_file: Optional[str] = None,
        log_level: LogLevel = LogLevel.INFO,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        db_table: str = "warnings",
        db_levels: Optional[List[LogLevel]] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        filters: Optional[List[Callable[[Dict[str, Any]], bool]]] = None
    ):
        """
        DiscordLogger 초기화
        
        매개변수:
            name (str): 로거 이름
            webhook_url (str, 선택): Discord 웹훅 URL
            webhook_levels (List[LogLevel], 선택): 웹훅을 보낼 로그 레벨 목록
            log_file (str, 선택): 로그 파일 경로
            log_level (LogLevel, 선택): 출력할 최소 로그 레벨 (기본값: INFO)
            supabase_url (str, 선택): Supabase 프로젝트 URL
            supabase_key (str, 선택): Supabase API 키
            db_table (str, 선택): 로그를 저장할 테이블 이름 (기본값: warnings)
            db_levels (List[LogLevel], 선택): Supabase에 저장할 로그 레벨 목록 (기본값: WARNING 이상)
            max_bytes (int, 선택): 로그 파일 최대 크기 (기본값: 10MB)
            backup_count (int, 선택): 보관할 백업 파일 수 (기본값: 5)
            filters (List[Callable], 선택): 로그 필터 함수 목록
        """
        self.name = name
        self.webhook_url = webhook_url or os.getenv('DISCORD_WEBHOOK_URL')
        self.webhook_levels = webhook_levels or [LogLevel.ERROR, LogLevel.CRITICAL]
        self.db_levels = db_levels or [LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        self.filters = filters or []
        
        # Supabase 클라이언트 초기화
        self.supabase: Optional[Client] = None
        if supabase_url and supabase_key:
            self.supabase = create_client(supabase_url, supabase_key)
        elif os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
            self.supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_KEY')
            )
        
        self.db_table = db_table
        
        # 로깅 설정
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.value)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level.value)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 설정 (지정된 경우)
        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(log_level.value)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def set_level(self, level: LogLevel):
        """콘솔과 파일 출력을 위한 최소 로그 레벨 설정"""
        self.logger.setLevel(level.value)
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
    
    def set_webhook_levels(self, levels: List[LogLevel]):
        """웹훅 알림을 보낼 로그 레벨 설정"""
        self.webhook_levels = levels
    
    def add_filter(self, filter_func: Callable[[Dict[str, Any]], bool]):
        """로그 필터 추가"""
        self.filters.append(filter_func)
    
    def set_db_levels(self, levels: List[LogLevel]):
        """Supabase에 저장할 로그 레벨 설정"""
        self.db_levels = levels
    
    def _format_message(self, message: str, **kwargs) -> str:
        """메시지 포맷팅"""
        return message.format(**kwargs)
    
    def _should_log(self, context: Dict[str, Any]) -> bool:
        """필터를 통과하는지 확인"""
        return all(filter_func(context) for filter_func in self.filters)
    
    def _send_webhook(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """설정된 레벨에 따라 Discord 웹훅으로 메시지 전송"""
        if self.webhook_url and level in self.webhook_levels and self._should_log(context):
            try:
                embed = {
                    "title": f"{level.name} 로그",
                    "description": message,
                    "color": self._get_color_for_level(level),
                    "timestamp": datetime.utcnow().isoformat(),
                    "fields": [
                        {"name": key, "value": str(value), "inline": True}
                        for key, value in context.items()
                    ]
                }
                
                payload = {
                    "embeds": [embed]
                }
                
                requests.post(self.webhook_url, json=payload)
            except Exception as e:
                self.logger.error(f"웹훅 전송 실패: {str(e)}")
    
    async def _send_webhook_async(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """비동기적으로 Discord 웹훅으로 메시지 전송"""
        if self.webhook_url and level in self.webhook_levels and self._should_log(context):
            try:
                embed = {
                    "title": f"{level.name} 로그",
                    "description": message,
                    "color": self._get_color_for_level(level),
                    "timestamp": datetime.utcnow().isoformat(),
                    "fields": [
                        {"name": key, "value": str(value), "inline": True}
                        for key, value in context.items()
                    ]
                }
                
                payload = {
                    "embeds": [embed]
                }
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: requests.post(self.webhook_url, json=payload)
                )
            except Exception as e:
                self.logger.error(f"웹훅 전송 실패: {str(e)}")
    
    def _save_to_db(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """로그를 Supabase 데이터베이스에 저장"""
        if self.supabase and level in self.db_levels and self._should_log(context):
            try:
                data = {
                    "level": level.name,
                    "message": message,
                    "logger_name": self.name,
                    "created_at": datetime.utcnow().isoformat(),
                    "context": context
                }
                self.supabase.table(self.db_table).insert(data).execute()
            except Exception as e:
                self.logger.error(f"데이터베이스 저장 실패: {str(e)}")
    
    async def _save_to_db_async(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """비동기적으로 로그를 Supabase 데이터베이스에 저장"""
        if self.supabase and level in self.db_levels and self._should_log(context):
            try:
                data = {
                    "level": level.name,
                    "message": message,
                    "logger_name": self.name,
                    "created_at": datetime.utcnow().isoformat(),
                    "context": context
                }
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.supabase.table(self.db_table).insert(data).execute()
                )
            except Exception as e:
                self.logger.error(f"데이터베이스 저장 실패: {str(e)}")
    
    def _get_color_for_level(self, level: LogLevel) -> int:
        """로그 레벨에 따른 Discord 임베드 색상 반환"""
        colors = {
            LogLevel.DEBUG: 0x808080,    # 회색
            LogLevel.INFO: 0x00FF00,     # 초록색
            LogLevel.WARNING: 0xFFFF00,  # 노란색
            LogLevel.ERROR: 0xFF0000,    # 빨간색
            LogLevel.CRITICAL: 0xFF0000  # 빨간색
        }
        return colors.get(level, 0x808080)
    
    def debug(self, message: str, **kwargs):
        """디버그 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.debug(formatted_message)
        self._send_webhook(LogLevel.DEBUG, formatted_message, context)
        self._save_to_db(LogLevel.DEBUG, formatted_message, context)
    
    def info(self, message: str, **kwargs):
        """정보 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.info(formatted_message)
        self._send_webhook(LogLevel.INFO, formatted_message, context)
        self._save_to_db(LogLevel.INFO, formatted_message, context)
    
    def warning(self, message: str, **kwargs):
        """경고 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.warning(formatted_message)
        self._send_webhook(LogLevel.WARNING, formatted_message, context)
        self._save_to_db(LogLevel.WARNING, formatted_message, context)
    
    def error(self, message: str, **kwargs):
        """오류 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.error(formatted_message)
        self._send_webhook(LogLevel.ERROR, formatted_message, context)
        self._save_to_db(LogLevel.ERROR, formatted_message, context)
    
    def critical(self, message: str, **kwargs):
        """심각한 오류 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.critical(formatted_message)
        self._send_webhook(LogLevel.CRITICAL, formatted_message, context)
        self._save_to_db(LogLevel.CRITICAL, formatted_message, context)
    
    async def async_debug(self, message: str, **kwargs):
        """비동기 디버그 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.debug(formatted_message)
        await self._send_webhook_async(LogLevel.DEBUG, formatted_message, context)
        await self._save_to_db_async(LogLevel.DEBUG, formatted_message, context)
    
    async def async_info(self, message: str, **kwargs):
        """비동기 정보 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.info(formatted_message)
        await self._send_webhook_async(LogLevel.INFO, formatted_message, context)
        await self._save_to_db_async(LogLevel.INFO, formatted_message, context)
    
    async def async_warning(self, message: str, **kwargs):
        """비동기 경고 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.warning(formatted_message)
        await self._send_webhook_async(LogLevel.WARNING, formatted_message, context)
        await self._save_to_db_async(LogLevel.WARNING, formatted_message, context)
    
    async def async_error(self, message: str, **kwargs):
        """비동기 오류 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.error(formatted_message)
        await self._send_webhook_async(LogLevel.ERROR, formatted_message, context)
        await self._save_to_db_async(LogLevel.ERROR, formatted_message, context)
    
    async def async_critical(self, message: str, **kwargs):
        """비동기 심각한 오류 레벨 로그 메시지 출력"""
        formatted_message = self._format_message(message, **kwargs)
        context = kwargs
        self.logger.critical(formatted_message)
        await self._send_webhook_async(LogLevel.CRITICAL, formatted_message, context)
        await self._save_to_db_async(LogLevel.CRITICAL, formatted_message, context)

class Logger:
    """로거 클래스"""
    def __init__(
        self,
        name: str,
        webhook_url: Optional[str] = None,
        webhook_levels: Optional[List[LogLevel]] = None,
        log_file: Optional[str] = None,
        log_level: LogLevel = LogLevel.INFO,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        db_table: str = "warnings",
        db_levels: Optional[List[LogLevel]] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        filters: Optional[List[Callable[[Dict[str, Any]], bool]]] = None
    ):
        """로거 초기화"""
        self.config = LoggerConfig(
            name=name,
            webhook_url=webhook_url,
            webhook_levels=webhook_levels,
            log_file=log_file,
            log_level=log_level,
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            db_table=db_table,
            db_levels=db_levels,
            max_bytes=max_bytes,
            backup_count=backup_count,
            filters=filters
        )
        
        self.handlers: List[BaseHandler] = []
        self._init_handlers()
    
    def _init_handlers(self):
        """핸들러 초기화"""
        # Discord 웹훅 핸들러
        if self.config.webhook_url:
            self.handlers.append(
                DiscordWebhookHandler(
                    name=self.config.name,
                    webhook_url=self.config.webhook_url,
                    webhook_levels=self.config.webhook_levels,
                    log_level=self.config.log_level
                )
            )
        
        # Supabase 핸들러
        if self.config.supabase_url and self.config.supabase_key:
            self.handlers.append(
                SupabaseHandler(
                    name=self.config.name,
                    supabase_url=self.config.supabase_url,
                    supabase_key=self.config.supabase_key,
                    db_table=self.config.db_table,
                    db_levels=self.config.db_levels,
                    log_level=self.config.log_level
                )
            )
        
        # 파일 핸들러
        if self.config.log_file:
            self.handlers.append(
                FileHandler(
                    name=self.config.name,
                    log_file=self.config.log_file,
                    max_bytes=self.config.max_bytes,
                    backup_count=self.config.backup_count,
                    log_level=self.config.log_level
                )
            )
        
        # 필터 설정
        for handler in self.handlers:
            for filter_func in self.config.filters:
                handler.add_filter(filter_func)
    
    def set_level(self, level: LogLevel):
        """로그 레벨 설정"""
        self.config.log_level = level
        for handler in self.handlers:
            if isinstance(handler, FileHandler):
                handler.logger.setLevel(level.value)
    
    def set_webhook_levels(self, levels: List[LogLevel]):
        """웹훅 알림을 보낼 로그 레벨 설정"""
        self.config.webhook_levels = levels
        for handler in self.handlers:
            if isinstance(handler, DiscordWebhookHandler):
                handler.webhook_levels = levels
    
    def set_db_levels(self, levels: List[LogLevel]):
        """Supabase에 저장할 로그 레벨 설정"""
        self.config.db_levels = levels
        for handler in self.handlers:
            if isinstance(handler, SupabaseHandler):
                handler.db_levels = levels
    
    def add_filter(self, filter_func: Callable[[Dict[str, Any]], bool]):
        """로그 필터 추가"""
        self.config.filters.append(filter_func)
        for handler in self.handlers:
            handler.add_filter(filter_func)
    
    def _create_log_method(self, level: LogLevel):
        """로그 메서드 생성"""
        def log_method(self, message: str, **kwargs):
            formatted_message = format_message(message, **kwargs)
            context = kwargs
            
            for handler in self.handlers:
                handler.log(level, formatted_message, context)
        
        return log_method
    
    def _create_async_log_method(self, level: LogLevel):
        """비동기 로그 메서드 생성"""
        async def async_log_method(self, message: str, **kwargs):
            formatted_message = format_message(message, **kwargs)
            context = kwargs
            
            for handler in self.handlers:
                await handler.log_async(level, formatted_message, context)
        
        return async_log_method

# 로그 레벨별 메서드 동적 생성
for level in LogLevel:
    setattr(Logger, level.name.lower(), _create_log_method(level))
    setattr(Logger, f"async_{level.name.lower()}", _create_async_log_method(level)) 