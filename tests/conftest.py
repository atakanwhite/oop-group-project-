import pytest

import db


@pytest.fixture
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_snekPM.db"
    monkeypatch.setattr(db, "DATABASE_FILE", str(test_db))
    db.init_db()
    yield
