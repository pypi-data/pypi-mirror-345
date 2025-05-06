# config/app_config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


APP_NAME = os.getenv("APP_NAME", "My Application")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv('ENV')
API_BASE = os.getenv('API_BASE')
