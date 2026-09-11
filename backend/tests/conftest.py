import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text
from database import get_session
from main import app
from datetime import date
from sqlalchemy.pool import StaticPool
import models

# In-memory SQLite for tests
TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

def get_test_session():
    with Session(TEST_ENGINE) as session:
        yield session

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(TEST_ENGINE)
    with Session(TEST_ENGINE) as session:
        # Enable foreign keys for sqlite
        session.execute(text("PRAGMA foreign_keys=ON"))
        yield session
    SQLModel.metadata.drop_all(TEST_ENGINE)

@pytest.fixture(name="client")
def client_fixture(session):
    def override():
        yield session
    app.dependency_overrides[get_session] = override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
