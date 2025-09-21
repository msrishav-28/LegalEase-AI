#!/usr/bin/env python3
"""Startup script for Celery worker with proper configuration."""

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
    """Start the Celery worker."""
    settings = get_settings()
    
    logger.info("Starting LegalEase AI Celery Worker")
    logger.info(f"Broker URL: {settings.rabbitmq_url}")
    logger.info(f"Result Backend: {settings.redis_url}")
    
    # Worker configuration
    worker_args = [
        'worker',
        '--app=app.celery_app.celery:celery_app',
        '--loglevel=info',
        '--concurrency=4',
        '--queues=document_processing,ai_analysis,jurisdiction_analysis,celery',
        '--hostname=legalease-worker@%h',
        '--max-tasks-per-child=1000',
        '--time-limit=600',
        '--soft-time-limit=300',
    ]
    
    # Add optimization flags
    if not settings.debug:
        worker_args.extend([
            '--optimization=fair',
            '--prefetch-multiplier=1',
        ])
    
    try:
        # Start the worker
        celery_app.worker_main(worker_args)
    except KeyboardInterrupt:
        logger.info("Celery worker stopped by user")
    except Exception as exc:
        logger.error(f"Celery worker failed: {exc}")
        sys.exit(1)


if __name__ == '__main__':
    main()