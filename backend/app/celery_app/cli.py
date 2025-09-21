"""Command-line interface for Celery worker management."""

import click
import json
from typing import Optional
from datetime import datetime

from app.celery_app.celery import celery_app
from app.celery_app.monitoring import task_monitor, retry_manager


@click.group()
def celery_cli():
    """LegalEase AI Celery management commands."""
    pass


@celery_cli.command()
@click.option('--task-id', required=True, help='Task ID to check')
def status(task_id: str):
    """Get the status of a specific task."""
    try:
        status_info = task_monitor.get_task_status(task_id)
        click.echo(json.dumps(status_info, indent=2))
    except Exception as exc:
        click.echo(f"Error getting task status: {exc}", err=True)


@celery_cli.command()
def active():
    """List all active tasks."""
    try:
        active_tasks = task_monitor.get_active_tasks()
        if not active_tasks:
            click.echo("No active tasks found.")
        else:
            click.echo(f"Found {len(active_tasks)} active tasks:")
            for task in active_tasks:
                click.echo(f"  - {task['task_id']}: {task['name']} (worker: {task['worker']})")
    except Exception as exc:
        click.echo(f"Error getting active tasks: {exc}", err=True)


@celery_cli.command()
def scheduled():
    """List all scheduled tasks."""
    try:
        scheduled_tasks = task_monitor.get_scheduled_tasks()
        if not scheduled_tasks:
            click.echo("No scheduled tasks found.")
        else:
            click.echo(f"Found {len(scheduled_tasks)} scheduled tasks:")
            for task in scheduled_tasks:
                click.echo(f"  - {task['task_id']}: {task['name']} (ETA: {task.get('eta', 'N/A')})")
    except Exception as exc:
        click.echo(f"Error getting scheduled tasks: {exc}", err=True)


@celery_cli.command()
def workers():
    """Show worker statistics."""
    try:
        stats = task_monitor.get_worker_stats()
        click.echo(f"Active workers: {stats['workers']}")
        
        if stats['workers'] > 0:
            for worker, info in stats['details'].items():
                click.echo(f"\nWorker: {worker}")
                click.echo(f"  Status: {info['status']}")
                if 'total_tasks' in info:
                    total = info['total_tasks']
                    click.echo(f"  Total tasks: {total}")
    except Exception as exc:
        click.echo(f"Error getting worker stats: {exc}", err=True)


@celery_cli.command()
@click.option('--task-id', required=True, help='Task ID to cancel')
@click.option('--terminate', is_flag=True, help='Terminate task forcefully')
def cancel(task_id: str, terminate: bool):
    """Cancel a running task."""
    try:
        result = task_monitor.cancel_task(task_id, terminate=terminate)
        if result['status'] == 'success':
            action = result['action']
            click.echo(f"Task {task_id} has been {action}.")
        else:
            click.echo(f"Failed to cancel task {task_id}: {result.get('error', 'Unknown error')}", err=True)
    except Exception as exc:
        click.echo(f"Error canceling task: {exc}", err=True)


@celery_cli.command()
@click.option('--queue', help='Queue name to purge (default: all queues)')
@click.confirmation_option(prompt='Are you sure you want to purge the queue(s)?')
def purge(queue: Optional[str]):
    """Purge tasks from queue(s)."""
    try:
        result = task_monitor.purge_queue(queue)
        if result['status'] == 'success':
            queue_name = result['queue']
            click.echo(f"Successfully purged queue: {queue_name}")
        else:
            click.echo(f"Failed to purge queue: {result.get('error', 'Unknown error')}", err=True)
    except Exception as exc:
        click.echo(f"Error purging queue: {exc}", err=True)


@celery_cli.command()
@click.option('--task-name', help='Specific task name to retry')
@click.option('--max-age-hours', default=24, help='Maximum age of failed tasks to retry (hours)')
def retry_failed(task_name: Optional[str], max_age_hours: int):
    """Retry failed tasks."""
    try:
        result = retry_manager.retry_failed_tasks(task_name, max_age_hours)
        if result['status'] == 'success':
            retried = result['retried_tasks']
            click.echo(f"Successfully retried {retried} failed tasks.")
        else:
            click.echo(f"Failed to retry tasks: {result.get('error', 'Unknown error')}", err=True)
    except Exception as exc:
        click.echo(f"Error retrying failed tasks: {exc}", err=True)


@celery_cli.command()
@click.argument('document_id')
def process_document(document_id: str):
    """Queue a document for processing."""
    try:
        from app.celery_app.tasks.document_processing import process_document_task
        
        result = process_document_task.delay(document_id)
        click.echo(f"Document processing queued with task ID: {result.id}")
        click.echo(f"Use 'celery-cli status --task-id {result.id}' to check progress.")
    except Exception as exc:
        click.echo(f"Error queuing document processing: {exc}", err=True)


@celery_cli.command()
@click.argument('document_id')
def analyze_ai(document_id: str):
    """Queue a document for AI analysis."""
    try:
        from app.celery_app.tasks.ai_analysis import analyze_document_with_ai_task
        
        result = analyze_document_with_ai_task.delay(document_id)
        click.echo(f"AI analysis queued with task ID: {result.id}")
        click.echo(f"Use 'celery-cli status --task-id {result.id}' to check progress.")
    except Exception as exc:
        click.echo(f"Error queuing AI analysis: {exc}", err=True)


@celery_cli.command()
@click.argument('document_id')
def detect_jurisdiction(document_id: str):
    """Queue a document for jurisdiction detection."""
    try:
        from app.celery_app.tasks.jurisdiction_analysis import detect_document_jurisdiction_task
        
        result = detect_document_jurisdiction_task.delay(document_id)
        click.echo(f"Jurisdiction detection queued with task ID: {result.id}")
        click.echo(f"Use 'celery-cli status --task-id {result.id}' to check progress.")
    except Exception as exc:
        click.echo(f"Error queuing jurisdiction detection: {exc}", err=True)


@celery_cli.command()
def health_check():
    """Run system health check."""
    try:
        from app.celery_app.tasks.maintenance import health_check_task
        
        result = health_check_task.delay()
        click.echo(f"Health check queued with task ID: {result.id}")
        
        # Wait for result and display
        try:
            health_result = result.get(timeout=60)
            click.echo("\nHealth Check Results:")
            click.echo(f"Overall Status: {health_result['status']}")
            click.echo(f"Timestamp: {health_result['timestamp']}")
            
            click.echo("\nComponent Status:")
            for component, info in health_result['components'].items():
                status_color = 'green' if info['status'] == 'healthy' else 'red'
                click.echo(f"  {component}: ", nl=False)
                click.secho(info['status'], fg=status_color)
                if info.get('message'):
                    click.echo(f"    {info['message']}")
                    
        except Exception as exc:
            click.echo(f"Health check is running in background. Task ID: {result.id}")
            
    except Exception as exc:
        click.echo(f"Error running health check: {exc}", err=True)


@celery_cli.command()
def metrics():
    """Generate and display system metrics."""
    try:
        from app.celery_app.tasks.maintenance import generate_system_metrics_task
        
        result = generate_system_metrics_task.delay()
        click.echo(f"Metrics generation queued with task ID: {result.id}")
        
        # Wait for result and display
        try:
            metrics_result = result.get(timeout=60)
            click.echo("\nSystem Metrics:")
            click.echo(f"Timestamp: {metrics_result['timestamp']}")
            
            if 'documents' in metrics_result:
                docs = metrics_result['documents']
                click.echo(f"\nDocuments:")
                click.echo(f"  Total: {docs['total']}")
                click.echo(f"  Processed: {docs['processed']}")
                click.echo(f"  Processing Rate: {docs['processing_rate']:.1f}%")
            
            if 'analyses' in metrics_result:
                analyses = metrics_result['analyses']
                click.echo(f"\nAnalyses:")
                click.echo(f"  Total: {analyses['total']}")
                click.echo(f"  Recent (24h): {analyses['recent_24h']}")
            
            if 'jurisdictions' in metrics_result:
                jurisdictions = metrics_result['jurisdictions']
                click.echo(f"\nJurisdiction Distribution:")
                for jurisdiction, count in jurisdictions.items():
                    click.echo(f"  {jurisdiction}: {count}")
                    
        except Exception as exc:
            click.echo(f"Metrics generation is running in background. Task ID: {result.id}")
            
    except Exception as exc:
        click.echo(f"Error generating metrics: {exc}", err=True)


@celery_cli.command()
def cleanup():
    """Run cleanup of expired results."""
    try:
        from app.celery_app.tasks.maintenance import cleanup_expired_results_task
        
        result = cleanup_expired_results_task.delay()
        click.echo(f"Cleanup queued with task ID: {result.id}")
        
        # Wait for result and display
        try:
            cleanup_result = result.get(timeout=120)
            click.echo("\nCleanup Results:")
            click.echo(f"Status: {cleanup_result['status']}")
            click.echo(f"Cleaned analyses: {cleanup_result.get('cleaned_analyses', 0)}")
            click.echo(f"Cleaned jurisdiction analyses: {cleanup_result.get('cleaned_jurisdiction_analyses', 0)}")
            click.echo(f"Cleaned files: {cleanup_result.get('cleaned_files', 0)}")
            
        except Exception as exc:
            click.echo(f"Cleanup is running in background. Task ID: {result.id}")
            
    except Exception as exc:
        click.echo(f"Error running cleanup: {exc}", err=True)


@celery_cli.command()
@click.option('--queue', help='Show length of specific queue')
def queue_length(queue: Optional[str]):
    """Show queue lengths."""
    try:
        if queue:
            length = task_monitor.get_queue_length(queue)
            if length >= 0:
                click.echo(f"Queue '{queue}' length: {length}")
            else:
                click.echo(f"Error getting length for queue '{queue}'")
        else:
            # Show all queue lengths
            queues = ["document_processing", "ai_analysis", "jurisdiction_analysis", "celery"]
            click.echo("Queue lengths:")
            for q in queues:
                length = task_monitor.get_queue_length(q)
                if length >= 0:
                    click.echo(f"  {q}: {length}")
                else:
                    click.echo(f"  {q}: Error")
    except Exception as exc:
        click.echo(f"Error getting queue lengths: {exc}", err=True)


if __name__ == '__main__':
    celery_cli()