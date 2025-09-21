"""Celery application package for LegalEase AI."""

from app.celery_app.celery import celery_app

__all__ = ["celery_app"]