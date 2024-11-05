import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config 객체를 생성하여 .ini 파일 설정을 적용
config = context.config

# 로깅 설정 적용
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# 메타데이터 객체 추가 - 데이터베이스 마이그레이션에 필요한 모든 모델을 포함하는 객체
# 예를 들어, app/models/base.py에 선언된 Base를 사용한다고 가정합니다.
from app.models.base import Base  # 모델의 Base 클래스 임포트
target_metadata = Base.metadata

# 오프라인 모드로 마이그레이션을 실행하는 함수
def run_migrations_offline():
    """Run migrations in 'offline' mode.
    URL만 사용하여 데이터베이스 연결을 설정하며, 엔진을 생성하지 않습니다.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

# 온라인 모드로 마이그레이션을 실행하는 함수
def run_migrations_online():
    """Run migrations in 'online' mode.
    엔진을 생성하고 연결을 설정하여 데이터베이스에 접속합니다.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

# Alembic이 offline 모드인지 online 모드인지에 따라 적절한 함수를 호출
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
