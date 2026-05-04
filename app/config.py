import os
import logging

logger = logging.getLogger(__name__)

# All secrets loaded from environment variables
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION            = os.environ.get('AWS_REGION', 'us-east-1')
GITHUB_TOKEN          = os.environ.get('GITHUB_TOKEN')
API_KEY               = os.environ.get('API_KEY')
SECRET_KEY            = os.environ.get('SECRET_KEY')
DATABASE_URL          = os.environ.get('DATABASE_URL')
SLACK_WEBHOOK         = os.environ.get('SLACK_WEBHOOK')

# All critical secrets validated
REQUIRED_SECRETS = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'DATABASE_URL',
    'SECRET_KEY',
    'API_KEY',
]

def validate_config():
    missing = [k for k in REQUIRED_SECRETS if not os.environ.get(k)]
    if missing:
        logger.error('Missing required environment variables: %d', len(missing))
        raise EnvironmentError('Application configuration incomplete')

# Auto-validate on import in production
if os.environ.get('APP_ENV') == 'production':
    validate_config()
