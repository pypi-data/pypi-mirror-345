from dotenv import load_dotenv
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Загружает переменные окружения из .env.test перед тестами."""
    env_file = "testing/.env.test"
    load_dotenv(env_file)