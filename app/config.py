import os
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


# All secrets from environment variables only
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION            = os.environ.get('AWS_REGION', 'us-east-1')
GITHUB_TOKEN          = os.environ.get('GITHUB_TOKEN')
API_KEY               = os.environ.get('API_KEY')
SECRET_KEY            = os.environ.get('SECRET_KEY')
DATABASE_URL          = os.environ.get('DATABASE_URL')
SLACK_WEBHOOK         = os.environ.get('SLACK_WEBHOOK')

# Minimum lengths for security-critical secrets
_MIN_LENGTHS = {
    'SECRET_KEY': 32,
    'AWS_SECRET_ACCESS_KEY': 20,
    'API_KEY': 16,
}

# Required in all environments
_REQUIRED = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'DATABASE_URL',
    'SECRET_KEY',
    'API_KEY',
]


def validate_config():
    # Check required secrets present
    missing = [k for k in _REQUIRED if not os.environ.get(k)]
    if missing:
        logger.error('Application configuration incomplete')
        raise ConfigurationError('Application configuration incomplete')

    # Check minimum lengths for security-critical secrets
    for key, min_len in _MIN_LENGTHS.items():
        value = os.environ.get(key, '')
        if value and len(value) < min_len:
            logger.error('Application configuration incomplete')
            raise ConfigurationError('Application configuration incomplete')

    # Validate optional secrets format when provided
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url and not db_url.startswith(('postgresql://', 'mysql://', 'sqlite://')):
        logger.error('Application configuration incomplete')
        raise ConfigurationError('Application configuration incomplete')

    logger.info('Configuration validated successfully')


# Validate in all environments
validate_config()
