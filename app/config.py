import os

# ========================================
# Secure config - all secrets from environment variables
# ========================================

# AWS credentials — from environment
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION            = os.environ.get('AWS_REGION', 'us-east-1')

# GitHub token — from environment
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# API keys — from environment
API_KEY    = os.environ.get('API_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Database — from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

# Slack webhook — from environment
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK')

# Validate required secrets are present at startup
def validate_config():
    required = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'DATABASE_URL']
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {missing}")
