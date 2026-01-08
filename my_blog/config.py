"""
Configuration managment
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ====================================
# Paths
# ====================================

BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
STATIC_DIR = Path(os.environ.get('STATIC_DIR', PROJECT_ROOT / 'static'))
DATA_DIR = Path(os.environ.get('DATA_DIR', BASE_DIR / 'data'))
IMAGE_DIR = STATIC_DIR / 'image'
POST_IMAGE_DIR = IMAGE_DIR / 'post_images'

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
# Ensure static, image and post image  directories exists
STATIC_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)
POST_IMAGE_DIR.mkdir(exist_ok=True)

USERS_DB_NAME = os.environ.get('USERS_DB_NAME', 'users.db') 
USERS_DB_PATH = DATA_DIR / USERS_DB_NAME
POSTS_DB_NAME = os.environ.get('POSTS_DB_NAME', 'posts.db')
POSTS_DB_PATH = DATA_DIR / POSTS_DB_NAME

# ============================================
# Security
# ============================================

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION")

# Session configuration
SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY", "3600"))  # 1 hour default

# ============================================
# Authentication Settings
# ============================================

ALLOW_REGISTRATION = os.getenv("ALLOW_REGISTRATION", "False").lower() == "true"

# Initial admin user (for setup_db.py only)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")

# ============================================
# Application Settings
# ============================================

# Development mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
RELOAD = DEBUG
