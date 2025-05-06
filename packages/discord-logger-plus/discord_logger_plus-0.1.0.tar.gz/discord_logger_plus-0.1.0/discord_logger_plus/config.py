import os
from typing import Optional, List, Dict, Any
from .handlers import LogLevel

class LoggerConfig:
    """로거 설정을 관리하는 클래스"""
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
        filters: Optional[List[Dict[str, Any]]] = None
    ):
        self.name = name
        self.webhook_url = webhook_url or os.getenv('DISCORD_WEBHOOK_URL')
        self.webhook_levels = webhook_levels or [LogLevel.ERROR, LogLevel.CRITICAL]
        self.log_file = log_file
        self.log_level = log_level
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        self.db_table = db_table
        self.db_levels = db_levels or [LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.filters = filters or []
        
        self._validate_config()
    
    def _validate_config(self):
        """설정값 검증"""
        if not self.name:
            raise ValueError("Logger name is required")
        
        if self.webhook_url and not self.webhook_url.startswith('http'):
            raise ValueError("Invalid webhook URL")
        
        if self.supabase_url and not self.supabase_url.startswith('http'):
            raise ValueError("Invalid Supabase URL")
        
        if self.supabase_url and not self.supabase_key:
            raise ValueError("Supabase key is required when URL is provided")
        
        if self.log_file and not os.path.exists(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            'name': self.name,
            'webhook_url': self.webhook_url,
            'webhook_levels': self.webhook_levels,
            'log_file': self.log_file,
            'log_level': self.log_level,
            'supabase_url': self.supabase_url,
            'supabase_key': self.supabase_key,
            'db_table': self.db_table,
            'db_levels': self.db_levels,
            'max_bytes': self.max_bytes,
            'backup_count': self.backup_count,
            'filters': self.filters
        } 