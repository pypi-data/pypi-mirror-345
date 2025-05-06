import os
import logging
import requests
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any, Callable
from enum import Enum
from supabase import create_client, Client
from logging.handlers import RotatingFileHandler
from .templates import EmbedTemplate, LogEmbedTemplate, DEFAULT_TEMPLATES
from .utils import handle_errors, get_color_for_level, should_log, run_in_executor

class LogLevel(Enum):
    """로그 레벨을 정의하는 열거형"""
    DEBUG = 10    # 디버깅용 상세 정보
    INFO = 20     # 일반 정보
    WARNING = 30  # 경고 메시지
    ERROR = 40    # 오류 메시지
    CRITICAL = 50 # 심각한 오류 메시지

class BaseHandler:
    """기본 핸들러 클래스"""
    def __init__(self, name: str, log_level: LogLevel = LogLevel.INFO):
        self.name = name
        self.log_level = log_level
        self.filters: List[Callable[[Dict[str, Any]], bool]] = []
    
    def add_filter(self, filter_func: Callable[[Dict[str, Any]], bool]):
        """로그 필터 추가"""
        self.filters.append(filter_func)
    
    def _should_log(self, context: Dict[str, Any]) -> bool:
        """필터를 통과하는지 확인"""
        return should_log(context, self.filters)
    
    def _format_message(self, message: str, **kwargs) -> str:
        """메시지 포맷팅"""
        return message.format(**kwargs)

class DiscordWebhookHandler(BaseHandler):
    """Discord 웹훅 핸들러"""
    def __init__(
        self,
        name: str,
        webhook_url: Optional[str] = None,
        webhook_levels: Optional[List[LogLevel]] = None,
        log_level: LogLevel = LogLevel.INFO,
        templates: Optional[Dict[LogLevel, EmbedTemplate]] = None
    ):
        super().__init__(name, log_level)
        self.webhook_url = webhook_url or os.getenv('DISCORD_WEBHOOK_URL')
        self.webhook_levels = webhook_levels or [LogLevel.ERROR, LogLevel.CRITICAL]
        self.templates = templates or DEFAULT_TEMPLATES
    
    def set_template(self, level: LogLevel, template: EmbedTemplate):
        """특정 레벨의 템플릿 설정"""
        self.templates[level] = template
    
    def set_templates(self, templates: Dict[LogLevel, EmbedTemplate]):
        """템플릿 전체 설정"""
        self.templates = templates
    
    @handle_errors
    def log(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """웹훅으로 메시지 전송"""
        if not self._should_send_webhook(level, context):
            return
        
        context.update({
            "message": message,
            "logger_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.name
        })
        
        template = self.templates.get(level, DEFAULT_TEMPLATES[LogLevel.INFO])
        embed = template.to_dict(context)
        
        payload = {"embeds": [embed]}
        requests.post(self.webhook_url, json=payload)
    
    @handle_errors
    async def log_async(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """비동기적으로 웹훅으로 메시지 전송"""
        if not self._should_send_webhook(level, context):
            return
        
        context.update({
            "message": message,
            "logger_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.name
        })
        
        template = self.templates.get(level, DEFAULT_TEMPLATES[LogLevel.INFO])
        embed = template.to_dict(context)
        
        payload = {"embeds": [embed]}
        await run_in_executor(requests.post, self.webhook_url, json=payload)
    
    def _should_send_webhook(self, level: LogLevel, context: Dict[str, Any]) -> bool:
        """웹훅을 보내야 하는지 확인"""
        return bool(self.webhook_url and level in self.webhook_levels and self._should_log(context))

class SupabaseHandler(BaseHandler):
    """Supabase 데이터베이스 핸들러"""
    def __init__(
        self,
        name: str,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        db_table: str = "warnings",
        db_levels: Optional[List[LogLevel]] = None,
        log_level: LogLevel = LogLevel.INFO
    ):
        super().__init__(name, log_level)
        self.db_levels = db_levels or [LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        self.db_table = db_table
        self.supabase = self._init_supabase_client(supabase_url, supabase_key)
    
    def _init_supabase_client(self, supabase_url: Optional[str], supabase_key: Optional[str]) -> Optional[Client]:
        """Supabase 클라이언트 초기화"""
        if supabase_url and supabase_key:
            return create_client(supabase_url, supabase_key)
        elif os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
            return create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_KEY')
            )
        return None
    
    @handle_errors
    def log(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """로그를 Supabase 데이터베이스에 저장"""
        if not self._should_save_to_db(level, context):
            return
        
        data = self._create_db_data(level, message, context)
        self.supabase.table(self.db_table).insert(data).execute()
    
    @handle_errors
    async def log_async(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """비동기적으로 로그를 Supabase 데이터베이스에 저장"""
        if not self._should_save_to_db(level, context):
            return
        
        data = self._create_db_data(level, message, context)
        await run_in_executor(
            lambda: self.supabase.table(self.db_table).insert(data).execute()
        )
    
    def _should_save_to_db(self, level: LogLevel, context: Dict[str, Any]) -> bool:
        """데이터베이스에 저장해야 하는지 확인"""
        return bool(self.supabase and level in self.db_levels and self._should_log(context))
    
    def _create_db_data(self, level: LogLevel, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스 저장용 데이터 생성"""
        return {
            "level": level.name,
            "message": message,
            "logger_name": self.name,
            "created_at": datetime.utcnow().isoformat(),
            "context": context
        }

class FileHandler(BaseHandler):
    """파일 로깅 핸들러"""
    def __init__(
        self,
        name: str,
        log_file: str,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        log_level: LogLevel = LogLevel.INFO
    ):
        super().__init__(name, log_level)
        self.logger = self._init_logger(name, log_file, max_bytes, backup_count, log_level)
    
    def _init_logger(
        self,
        name: str,
        log_file: str,
        max_bytes: int,
        backup_count: int,
        log_level: LogLevel
    ) -> logging.Logger:
        """로거 초기화"""
        logger = logging.getLogger(name)
        logger.setLevel(log_level.value)
        
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
        logger.addHandler(file_handler)
        
        return logger
    
    def log(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """파일에 로그 메시지 출력"""
        if self._should_log(context):
            log_method = getattr(self.logger, level.name.lower())
            log_method(message)
    
    async def log_async(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """비동기적으로 파일에 로그 메시지 출력"""
        self.log(level, message, context) 