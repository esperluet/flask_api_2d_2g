from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

class Base(DeclarativeBase):
  pass

engine = create_engine(
    "postgresql+psycopg2://app:pass_word_12@db:5432/library"
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db_session():
   return SessionLocal()