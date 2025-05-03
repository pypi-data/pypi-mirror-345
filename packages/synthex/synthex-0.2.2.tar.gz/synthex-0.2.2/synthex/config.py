from typing import Callable
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Config(BaseSettings):
    
    API_KEY: str
    API_KEY_TIER_1: str
    
    OUTPUT_FILE_DEFAULT_NAME: Callable[[str], str] = lambda desired_format: f"synthex_output.{desired_format}"
    DEBUG_MODE: bool = False
    DEBUG_MODE_FOLDER: str = ".debug"
    
    class Config:
        env_file = ".env"
        env_prefix = ""
          
    
config = Config() # type: ignore
