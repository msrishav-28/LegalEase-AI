#!/usr/bin/env python3
"""Startup script for Celery Beat scheduler."""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.celery_app.celery import celery_app
from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start the Celery Beat scheduler."""
    settings = get_settings()
    
    logger.info("Starting LegalEase AI Celery Beat Scheduler")
    logger.info(f"Broker URL: {settings.rabbitmq_url}")
    
    # Beat configuration
    beat_args = [
        'beat',
        '--app=app.celery_app.celery:celery_app',
        '--loglevel=info',
        '--schedule=/tmp/celerybeat-schedule',
        '--pidfile=/tmp/celerybeat.pid',
    ]
    
    try:
        # Start the beat scheduler
        celery_app.start(beat_args)
    except KeyboardInterrupt:
        logger.info("Celery Beat scheduler stopped by user")
    except Exception as exc:
        logger.error(f"Celery Beat scheduler failed: {exc}")
        sys.exit(1)


if __name__ == '__main__':
    main()