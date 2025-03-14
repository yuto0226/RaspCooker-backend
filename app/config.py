# -*- encoding: utf-8 -*-

import os
from pathlib import Path


class Config(object):
    BASE_DIR = Path(__file__).resolve().parent

    SECRET_KEY = os.getenv('SECRET_KEY', 'this is secret')


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


# Load all possible configurations
configs = {
    'Production': ProductionConfig,
    'Development': DevelopmentConfig,
    'Test': TestingConfig
}
