import os
import random

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some random string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[CSFM]'
    FLASKY_MAIL_SENDER = 'CSFM Admin <cpmr@example.com>'
    FLASKY_ADMIN = os.environ.get('CSFM_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

INDICATORS = {
    'csfm': [
        'language', 'satisfied', 'whyunsatisfied', 'waitingtime',
        'attitude', 'cleanliness', 'drugavailability', 'missingdrug', 'suggestion'
    ]
}
INDICATORS_WITH_VAL_IN_CATEGORTY = {
    'csfm': ['satisfied', 'drugavailability']
}

REPORT_AGGREGATE_INIDICATORS = {
    'csfm': [
    ],
}

# The following are used for generating dummy data

INDICATOR_CATEGORY_MAPPING = {
    'csfm': {

    },

}

# the guide random generation
INDICATOR_THRESHOLD = {
    'language': random.randint(0, 100),
    'satisfied': random.randint(0, 20),
    'whyunsatisfied': random.randint(0, 40),
    'waitingtime': random.randint(0, 20),
    'attitude': random.randint(0, 100),
    'cleanliness': random.randint(0, 30),
    'drugavailability': random.randint(0, 60),
    'missingdrug': random.randint(0, 80),
    'suggestion': random.randint(0, 60)
}

INDICATOR_NAME_MAPPING = {
    'satisfied': 'Client Satisfaction',
    'drugavailability': 'Availability of Prescribed Medicine',

}
