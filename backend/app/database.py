import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

# A connection is opened only when a request or migration needs it.
engine = create_engine(os.getenv('DATABASE_URL', 'postgresql+psycopg://applytrail@localhost/applytrail'), pool_pre_ping=True, connect_args={'connect_timeout': 3} if not os.getenv('DATABASE_URL', '').startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine)

def get_db():
    with SessionLocal() as session:
        yield session
