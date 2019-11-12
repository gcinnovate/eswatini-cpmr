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
    SSL_REDIRECT = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

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
INDICATORS_WITH_VALUE_IN_CATEGORTY = {
    'csfm': [
        'language', 'satisfied', 'drugavailability', 'cleanliness', 'attitude', 'waitingtime'
    ]
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

INDICATOR_POSSIBLE_VALUES = {
    'csfm': {
        'language': ['English', 'Siswati'],
        'satisfied': ['Yes', 'No'],
        'whyunsatisfied': [
            'There are long queues',
            'Health workers are slow',
            'Rude health workers', 'facility is very far'
        ],
        'waitingtime': ['Less than 30 mins', '30 mins - 1 hr', '1 hr - 2 hrs', 'More than 2 hrs', 'N/A'],
        'attitude': ['Very Good', 'Good', 'Average', 'Poor', 'Very Poor'],
        'cleanliness': ['Very Good', 'Good', 'Average', 'Poor', 'Very Poor'],
        'drugavailability': ['Yes', 'No'],
        'missingdrug': [
            'Paracetamol', 'Lopinavir', 'Tenofovir', 'Nevirapine', 'Zolandolic Acid', 'Duphaston'
        ],
        'suggestion': [
            'Health workers should keep time',
            'More medicine should be stalked',
            'There should be more serving stations',
            'Toilets should be regularly cleaned',
            'Patients should be given due attention',
            'The infrastructure should be improved'
        ]
    }
}

INDICATOR_NAME_MAPPING = {
    'satisfied': 'Client Satisfaction',
    'drugavailability': 'Availability of Prescribed Medicine',
    'missingdrug': 'Missing Drug'

}

# RapidPro API root
RAPIDPRO_APIv2_ROOT = 'http://localhost:8000/api/v2/'
RAPIDPRO_API_TOKEN = ''

# CSFM generic English flow UUID
CSFM_GENERIC_FLOW_UUID = ''
try:
    from local_config import *
except ImportError:
    pass
