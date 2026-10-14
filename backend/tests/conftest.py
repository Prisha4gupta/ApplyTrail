import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from app.database import get_db, Base
from app.main import app

@pytest.fixture()
def client():
    url = os.getenv('TEST_DATABASE_URL')
    if url:
        # Destructive fixture is intentionally restricted to a dedicated database.
        from sqlalchemy.engine import make_url
        assert make_url(url).database == 'applytrail_test', 'Tests require database named applytrail_test'
        engine = create_engine(url)
    else:
        engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        @event.listens_for(engine, 'connect')
        def enable_fk(connection, record):
            connection.execute('PRAGMA foreign_keys=ON')
    # Test schema only. Production always uses Alembic; CI also verifies the migration first.
    Base.metadata.create_all(engine)
    def override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
    engine.dispose()
