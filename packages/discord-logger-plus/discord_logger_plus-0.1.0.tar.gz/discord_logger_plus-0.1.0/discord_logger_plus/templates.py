from typing import Dict, Any, Optional
from datetime import datetime
from .handlers import LogLevel

class EmbedTemplate:
    """Discord 웹훅 임베드 템플릿 기본 클래스"""
    def __init__(
        self,
        title: str,
        description: str,
        color: int,
        fields: Optional[Dict[str, str]] = None,
        footer: Optional[str] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None
    ):
        self.title = title
        self.description = description
        self.color = color
        self.fields = fields or {}
        self.footer = footer
        self.thumbnail = thumbnail
        self.image = image
    
    def to_dict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """템플릿을 Discord 임베드 형식으로 변환"""
        embed = {
            "title": self.title.format(**context),
            "description": self.description.format(**context),
            "color": self.color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {"name": key, "value": value.format(**context), "inline": True}
                for key, value in self.fields.items()
            ]
        }
        
        if self.footer:
            embed["footer"] = {"text": self.footer.format(**context)}
        
        if self.thumbnail:
            embed["thumbnail"] = {"url": self.thumbnail.format(**context)}
        
        if self.image:
            embed["image"] = {"url": self.image.format(**context)}
        
        return embed

class LogEmbedTemplate(EmbedTemplate):
    """로그 메시지용 임베드 템플릿"""
    def __init__(
        self,
        level: LogLevel,
        title_template: str = "{level} 로그",
        description_template: str = "{message}",
        fields_template: Optional[Dict[str, str]] = None,
        footer_template: Optional[str] = None
    ):
        colors = {
            LogLevel.DEBUG: 0x808080,    # 회색
            LogLevel.INFO: 0x00FF00,     # 초록색
            LogLevel.WARNING: 0xFFFF00,  # 노란색
            LogLevel.ERROR: 0xFF0000,    # 빨간색
            LogLevel.CRITICAL: 0xFF0000  # 빨간색
        }
        
        super().__init__(
            title=title_template,
            description=description_template,
            color=colors.get(level, 0x808080),
            fields=fields_template,
            footer=footer_template
        )
    
    def to_dict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["level"] = context.get("level", "UNKNOWN")
        return super().to_dict(context)

# 기본 템플릿들
DEFAULT_TEMPLATES = {
    LogLevel.DEBUG: LogEmbedTemplate(
        level=LogLevel.DEBUG,
        title_template="{level} 로그",
        description_template="```\n{message}\n```",
        fields_template={
            "Logger": "{logger_name}",
            "Time": "{timestamp}"
        }
    ),
    LogLevel.INFO: LogEmbedTemplate(
        level=LogLevel.INFO,
        title_template="{level} 로그",
        description_template="{message}",
        fields_template={
            "Logger": "{logger_name}",
            "Time": "{timestamp}"
        }
    ),
    LogLevel.WARNING: LogEmbedTemplate(
        level=LogLevel.WARNING,
        title_template="{level} 로그",
        description_template="**{message}**",
        fields_template={
            "Logger": "{logger_name}",
            "Time": "{timestamp}"
        }
    ),
    LogLevel.ERROR: LogEmbedTemplate(
        level=LogLevel.ERROR,
        title_template="{level} 로그",
        description_template="**{message}**",
        fields_template={
            "Logger": "{logger_name}",
            "Time": "{timestamp}",
            "Error": "{error}"
        }
    ),
    LogLevel.CRITICAL: LogEmbedTemplate(
        level=LogLevel.CRITICAL,
        title_template="{level} 로그",
        description_template="**{message}**",
        fields_template={
            "Logger": "{logger_name}",
            "Time": "{timestamp}",
            "Error": "{error}"
        }
    )
} 