import pytest
import os
import json
import bcrypt
from src.utils import user_manager

@pytest.fixture(autouse=True)
def setup_mock_file(tmp_path, monkeypatch):
    mock_file = tmp_path / "test_users.json"
    monkeypatch.setattr(user_manager, "FILE_PATH", str(mock_file))
    return mock_file

def test_load_users_not_exists(setup_mock_file):
    data = user_manager.load_users()
    assert data == {"users": []}
    assert os.path.exists(str(setup_mock_file))

def test_load_users_empty(setup_mock_file):
    with open(str(setup_mock_file), "w") as f:
        pass
    data = user_manager.load_users()
    assert data == {"users": []}

def test_load_users_invalid_json(setup_mock_file):
    with open(str(setup_mock_file), "w") as f:
        f.write("{json_invalido: sim")
    data = user_manager.load_users()
    assert data == {"users": []}

def test_add_user_success():
    success, msg = user_manager.add_user("testuser", "password123")
    assert success is True
    data = user_manager.load_users()
    assert len(data["users"]) == 1
    assert data["users"][0]["username"] == "testuser"
    assert "password123" not in data["users"][0]["password"] 

def test_add_user_duplicate():
    user_manager.add_user("testuser", "password123")
    success, msg = user_manager.add_user("testuser", "password456")
    assert success is False
    assert "já existe" in msg

def test_add_user_long_password():
    long_pass = "a" * 73
    success, msg = user_manager.add_user("testuser", long_pass)
    assert success is False
    assert "demasiado longa" in msg

def test_authenticate_success():
    user_manager.add_user("testuser", "password123")
    user = user_manager.authenticate("testuser", "password123")
    assert user is not None
    assert user["username"] == "testuser"

def test_authenticate_fail_wrong_password():
    user_manager.add_user("testuser", "password123")
    user = user_manager.authenticate("testuser", "wrongpass")
    assert user is None

def test_authenticate_fail_not_found():
    user = user_manager.authenticate("ghost", "password123")
    assert user is None

def test_delete_user_success():
    user_manager.add_user("testuser", "password123")
    success, msg = user_manager.delete_user("testuser")
    assert success is True
    data = user_manager.load_users()
    assert len(data["users"]) == 0

def test_delete_user_not_found():
    success, msg = user_manager.delete_user("ghost")
    assert success is False
    assert "não encontrado" in msg

def test_change_role_success():
    user_manager.add_user("testuser", "password123", "user")
    success, msg = user_manager.change_role("testuser", "admin")
    assert success is True
    data = user_manager.load_users()
    assert data["users"][0]["role"] == "admin"

def test_change_role_invalid():
    success, msg = user_manager.change_role("testuser", "superadmin")
    assert success is False
    assert "Role inválido" in msg

def test_change_role_not_found():
    success, msg = user_manager.change_role("ghost", "admin")
    assert success is False
    assert "não encontrado" in msg