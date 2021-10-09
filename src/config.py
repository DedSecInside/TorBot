"""
Core settings for TorBot.
"""
import os
from dotenv import load_dotenv

load_dotenv() # Loads environment variables from .env file

__version__ = '2.1.0'


HOST = os.getenv('HOST')
PORT = os.getenv('PORT')