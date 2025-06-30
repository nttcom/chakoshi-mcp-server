"""A .env.test file is required."""

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    print("\nLoading .env file for testing session...")
    load_dotenv("tests/.env.test", override=True, verbose=True)
    print("Environment variables loaded.")
