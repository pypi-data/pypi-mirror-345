# Discord Logger Plus

Discord Logger Plus는 실시간 로그 알림과 선택적으로 Supabase 데이터베이스 저장을 지원하는 Python 로깅 라이브러리예요.

## 특징

- **실시간 알림**: 서버 오류나 중요한 이벤트를 Discord 채널로 즉시 알림
- **선택적 DB 저장**: Supabase 설정 시 로그를 자동으로 데이터베이스에 저장
- **유연한 설정**: 로그 레벨별로 콘솔, 파일, 웹훅, DB 저장을 독립적으로 설정
- **비동기 처리**: 웹훅 전송과 DB 저장이 앱 성능에 영향 주지 않음
- **자동 관리**: 로그 파일 자동 로테이션으로 디스크 공간 관리
- **커스텀 템플릿**: Discord 메시지 포맷을 자유롭게 커스터마이징
- **필터링**: 특정 조건의 로그만 선택적으로 처리

## 빠른 시작

```python
from discord_logger_plus import Logger, LogLevel

# 로거 초기화 (Discord 웹훅만 사용)
logger = Logger(
    name="my_app",
    webhook_url="your_discord_webhook_url",
    log_file="app.log"
)

# Supabase 연동이 필요한 경우
logger = Logger(
    name="my_app",
    webhook_url="your_discord_webhook_url",
    log_file="app.log",
    supabase_url="your_supabase_url",  # 선택사항
    supabase_key="your_supabase_key"   # 선택사항
)

# 로그 메시지
logger.info("앱이 시작되었습니다")
logger.warning("서버 과부하", cpu_usage=90)
logger.error("데이터베이스 연결 실패", error="Connection timeout")

# 비동기 로깅
await logger.async_info("비동기 작업 완료")
```

## 환경 설정

Discord 웹훅은 필수, Supabase는 선택사항이예요:

```env
# 필수
DISCORD_WEBHOOK_URL=your_webhook_url

# 선택사항
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## 상세 설정

### 로거 옵션

```python
Logger(
    name="app_name",                    # 필수: 로거 이름
    webhook_url="url",                  # 선택: Discord 웹훅 URL
    webhook_levels=[LogLevel.ERROR],    # 선택: 웹훅으로 보낼 로그 레벨
    log_file="app.log",                 # 선택: 로그 파일 경로
    log_level=LogLevel.INFO,            # 선택: 최소 로그 레벨
    supabase_url="url",                 # 선택: Supabase URL
    supabase_key="key",                 # 선택: Supabase API 키
    db_table="logs",                    # 선택: 데이터베이스 테이블 이름
    db_levels=[LogLevel.WARNING],       # 선택: DB에 저장할 로그 레벨
    max_bytes=10485760,                 # 선택: 최대 로그 파일 크기 (10MB)
    backup_count=5,                     # 선택: 백업 파일 수
    filters=[custom_filter]             # 선택: 로그 필터
)
```

### 로그 레벨

- `DEBUG`: 디버깅용 상세 정보
- `INFO`: 일반 정보
- `WARNING`: 경고 메시지
- `ERROR`: 오류 메시지
- `CRITICAL`: 심각한 오류 메시지

## 고급 사용법

### 커스텀 템플릿

```python
from discord_logger_plus import Logger, LogLevel, LogEmbedTemplate

# 커스텀 템플릿 생성
error_template = LogEmbedTemplate(
    level=LogLevel.ERROR,
    title_template="{service} 오류 발생",
    description_template="```\n{message}\n```",
    fields_template={
        "서비스": "{service}",
        "시간": "{timestamp}",
        "오류": "{error}"
    }
)

logger = Logger("my_app")
logger.set_template(LogLevel.ERROR, error_template)
```

### 비동기 로깅

```python
import asyncio
from discord_logger_plus import Logger

async def main():
    logger = Logger("my_app")
    await logger.async_info("비동기 작업 완료")

asyncio.run(main())
```

### 로그 필터링

```python
def ip_filter(context: dict) -> bool:
    return context.get('ip') == '192.168.1.1'

logger = Logger("my_app")
logger.add_filter(ip_filter)
```

## Q&A

### Q: Discord 웹훅 URL은 어떻게 얻나요?
A: Discord 서버에서 채널 설정 > 연동 > 웹훅 > 새 웹훅을 통해 생성할 수 있어요.

### Q: 로그 레벨은 어떻게 설정하나요?
A: `set_level()`, `set_webhook_levels()`, `set_db_levels()` 메서드를 사용해서 각각 설정할 수 있어요:
```python
logger.set_level(LogLevel.INFO)  # 콘솔 출력 레벨
logger.set_webhook_levels([LogLevel.ERROR, LogLevel.CRITICAL])  # 웹훅 전송 레벨
logger.set_db_levels([LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL])  # DB 저장 레벨
```

### Q: Supabase 없이 사용할 수 있나요?
A: 네, Supabase는 선택사항이예요. Discord 웹훅만 사용하고 싶다면 `supabase_url`과 `supabase_key`를 설정하지 않으면 돼요.

### Q: 로그 파일이 너무 커지면 어떻게 되나요?
A: `max_bytes`와 `backup_count` 설정으로 자동 관리돼요. 기본값은 10MB 크기 제한과 5개의 백업 파일이예요.

### Q: 비동기 로깅은 언제 사용하나요?
A: 웹훅 전송이나 DB 저장이 앱 성능에 영향을 줄 수 있을 때 사용해요. `async_` 접두사가 붙은 메서드를 사용하면 돼요:
```python
await logger.async_info("비동기 로그")
```

### Q: 로그에 추가 정보를 포함할 수 있나요?
A: 네, 모든 로그 메서드에 키워드 인자로 추가 정보를 전달할 수 있어요:
```python
logger.warning("서버 과부하", cpu_usage=90, memory_usage=85)
```

### Q: 특정 조건의 로그만 저장할 수 있나요?
A: 네, `add_filter()` 메서드로 필터 함수를 추가할 수 있어요:
```python
def ip_filter(context: dict) -> bool:
    return context.get('ip') == '192.168.1.1'
logger.add_filter(ip_filter)
```

## 기여하기

기여는 언제나 환영해요! [기여 가이드](CONTRIBUTING.md)를 읽어보시고 기여해주세요.

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고해주세요.
