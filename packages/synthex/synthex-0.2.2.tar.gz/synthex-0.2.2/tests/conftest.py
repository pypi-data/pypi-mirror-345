import pytest
import os
from dotenv import load_dotenv
from typing import Any, Literal
import shutil
from pathlib import Path
from typing import Generator

from synthex import Synthex
from synthex.config import config


load_dotenv()


def fetch_synthex(user_plan: Literal["TIER_1", "TIER_2"] = "TIER_2") -> Synthex:
    """
    Creates and returns an instance of the Synthex class using the API key 
    from the environment variables.
    Returns:
        Synthex: An instance of the Synthex class initialized with the API key.
    """
    
    api_key = config.API_KEY if user_plan == "TIER_2" else config.API_KEY_TIER_1
    if not api_key:
        pytest.fail("API_KEY not found in environment variables")
    return Synthex(api_key)


@pytest.fixture(scope="session")
def synthex(request: pytest.FixtureRequest) -> Synthex:
    """
    Creates and returns an instance of the Synthex class using the API key 
    from the environment variables.
    Returns:
        Synthex: An instance of the Synthex class initialized with the API key.
    """
    
    user_plan = getattr(request, "param", "TIER_2")
    if user_plan not in ("TIER_1", "TIER_2"):
        pytest.fail(f"Invalid user_plan: {user_plan}")
    
    return fetch_synthex(user_plan=user_plan)


@pytest.fixture(scope="function")
def short_lived_synthex(request: pytest.FixtureRequest) -> Synthex:
    """
    A short-lived version of the synthex fixture which is only valid for the duration of a test function.
    Returns:
        Synthex: An instance of the Synthex class initialized with the API key.
    """
    
    user_plan = getattr(request, "param", "TIER_2")
    if user_plan not in ("TIER_1", "TIER_2"):
        pytest.fail(f"Invalid user_plan: {user_plan}")
    
    return fetch_synthex()


@pytest.fixture(scope="session")
def generate_data_params() -> dict[Any, Any]:
    """
    Fixture to provide parameters for the generate_data method.
    Returns:
        dict: A dictionary containing the required data.
    """
    
    return {
        "schema_definition": {
            "question": {"type": "string"},
            "option-a": {"type": "string"},
            "option-b": {"type": "string"},
            "option-c": {"type": "string"},
            "option-d": {"type": "string"},
            "answer": {"type": "string"}
        },
        "examples": [
            {
                "question": "A gas occupies 6.0 L at 300 K and 1 atm. What is its volume at 600 K and 0.5 atm, assuming ideal gas behavior?",
                "option-a": "12.0 L",
                "option-b": "24.0 L",
                "option-c": "6.0 L",
                "option-d": "3.0 L",
                "answer": "option-b"
            }
        ],
        "requirements": [
            "Question Type: Multiple-choice questions (MCQs)",
            "Difficulty Level: High difficulty, comparable to SAT or AIEEE (JEE Main)",
            "Topic Coverage: Wide range of chemistry topics (physical, organic, inorganic)",
            "Number of Options: Each question must have four answer options",
            "Correct Answer: One of the four options must be correct and clearly marked",
            "Calculation-Based: Include mathematical/calculation-based questions",
            "Indirect Approach: Questions should be indirect and require knowledge application",
            "Conceptual Focus: Emphasize conceptual understanding, problem-solving, and analytical thinking"
        ],
        "number_of_samples": 20,
        "output_type": "csv",
        "output_path": f"test_data/output.csv"
    }
    
    

@pytest.fixture(autouse=True)
def isolate_env(tmp_path: Path = Path(".pytest_env_backup")) -> Generator[None, None, None]:
    """
    A pytest fixture that backs up the .env file before each test and restores it afterward.
    It uses a local temporary path to store the backup and ensures the directory is cleaned up after the test.
    Args:
        tmp_path (Path): Path used to temporarily store the .env backup.
    Yields:
        None
    """
    backup_file = tmp_path / ".env.bak"
    tmp_path.mkdir(parents=True, exist_ok=True)

    if os.path.exists(".env"):
        shutil.copy(".env", backup_file)

    yield  # Run the test

    if backup_file.exists():
        shutil.copy(backup_file, ".env")

    # Clean up backup directory
    shutil.rmtree(tmp_path, ignore_errors=True)