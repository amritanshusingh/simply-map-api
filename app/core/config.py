import os

class Settings:
    MODE = os.getenv('MODE', 'PROD')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

settings = Settings()
