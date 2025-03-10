import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    UPLOAD_FOLDER = 'temp_credentials'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    DEBUG = False
    TESTING = False
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    pass

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Use environment or default to development
config_name = os.environ.get('FLASK_ENV', 'development')
current_config = config[config_name]