# LegalEase AI Celery Worker System

This directory contains the Celery worker system for LegalEase AI, providing background task processing for document analysis, AI operations, and jurisdiction-specific legal processing.

## Architecture

The Celery system is organized into several components:

### Core Components

- **`celery.py`**: Main Celery application configuration and setup
- **`monitoring.py`**: Task monitoring and management utilities
- **`cli.py`**: Command-line interface for worker management

### Task Modules

- **`tasks/document_processing.py`**: Document upload, text extraction, and structure analysis
- **`tasks/ai_analysis.py`**: AI-powered document analysis and summarization
- **`tasks/jurisdiction_analysis.py`**: Jurisdiction detection and legal system analysis
- **`tasks/maintenance.py`**: System maintenance and monitoring tasks

### Queue Organization

The system uses multiple queues for different types of tasks:

- **`document_processing`**: File upload, text extraction, OCR processing
- **`ai_analysis`**: AI/ML operations, summarization, entity extraction
- **`jurisdiction_analysis`**: Legal jurisdiction detection and analysis
- **`celery`**: Default queue for general tasks

## Configuration

### Environment Variables

The system uses the following environment variables (configured in `app/config.py`):

```bash
# Message Broker
RABBITMQ_URL=amqp://legalease_user:legalease_password@localhost:5672/

# Result Backend
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_URL=postgresql+asyncpg://legalease_user:legalease_password@localhost:5432/legalease_ai

# AI Services
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
```

### Celery Configuration

Key configuration settings:

- **Task Serialization**: JSON format for cross-platform compatibility
- **Result Expiration**: 1 hour for temporary results
- **Worker Limits**: 5-minute soft limit, 10-minute hard limit per task
- **Retry Policy**: 3 retries with 1-minute delay
- **Prefetch**: 1 task per worker to ensure fair distribution

## Usage

### Starting Workers

#### Using Docker Compose (Recommended)

```bash
# Start all services including Celery worker
docker-compose up -d

# View Celery worker logs
docker-compose logs -f celery-worker
```

#### Manual Startup

```bash
# Start Celery worker
python scripts/start_celery_worker.py

# Start Celery Beat scheduler (for periodic tasks)
python scripts/start_celery_beat.py
```

#### Using Celery CLI

```bash
# Start worker with specific queues
celery -A app.celery_app worker --loglevel=info --queues=document_processing,ai_analysis

# Start Beat scheduler
celery -A app.celery_app beat --loglevel=info
```

### Task Management

#### Using the CLI Tool

```bash
# Check task status
python -m app.celery_app.cli status --task-id <task-id>

# List active tasks
python -m app.celery_app.cli active

# Show worker statistics
python -m app.celery_app.cli workers

# Cancel a task
python -m app.celery_app.cli cancel --task-id <task-id>

# Run health check
python -m app.celery_app.cli health-check

# Generate system metrics
python -m app.celery_app.cli metrics
```

#### Programmatic Usage

```python
from app.celery_app.tasks.document_processing import process_document_task
from app.celery_app.tasks.ai_analysis import analyze_document_with_ai_task
from app.celery_app.monitoring import task_monitor

# Queue document processing
result = process_document_task.delay("document-id-123")
print(f"Task queued: {result.id}")

# Check task progress
status = task_monitor.get_task_status(result.id)
print(f"Task status: {status['state']}")

# Queue AI analysis
ai_result = analyze_document_with_ai_task.delay("document-id-123")
```

## Task Types

### Document Processing Tasks

1. **`process_document_task`**: Complete document processing pipeline
   - Text extraction from PDF
   - Structure analysis
   - Metadata extraction

2. **`extract_document_text_task`**: Text extraction only
3. **`analyze_document_structure_task`**: Structure analysis only
4. **`batch_process_documents_task`**: Batch processing multiple documents

### AI Analysis Tasks

1. **`analyze_document_with_ai_task`**: Comprehensive AI analysis
   - Executive summary generation
   - Risk identification
   - Obligation extraction
   - Complexity scoring

2. **`generate_document_summary_task`**: Summary generation
3. **`extract_document_entities_task`**: Entity extraction
4. **`create_document_embeddings_task`**: Vector embeddings for search

### Jurisdiction Analysis Tasks

1. **`detect_document_jurisdiction_task`**: Automatic jurisdiction detection
2. **`analyze_indian_legal_document_task`**: Indian legal system analysis
3. **`analyze_us_legal_document_task`**: US legal system analysis
4. **`perform_cross_border_analysis_task`**: Cross-border legal comparison
5. **`comprehensive_jurisdiction_analysis_task`**: Complete jurisdiction workflow

### Maintenance Tasks

1. **`cleanup_expired_results_task`**: Clean up old analysis results
2. **`health_check_task`**: System health monitoring
3. **`generate_system_metrics_task`**: Performance metrics
4. **`optimize_database_task`**: Database optimization

## Monitoring and Debugging

### Task Progress Tracking

Tasks support real-time progress tracking:

```python
from app.celery_app.celery import TaskProgress

# In a task
TaskProgress.update_progress(task_id, 50, 100, "Processing document")

# Check progress
progress = TaskProgress.get_progress(task_id)
print(f"Progress: {progress['percentage']}% - {progress['message']}")
```

### Error Handling

The system includes comprehensive error handling:

- **Automatic Retries**: Failed tasks are retried up to 3 times
- **Error Logging**: Detailed error information is logged
- **Graceful Degradation**: Partial failures don't crash the entire pipeline
- **Custom Exceptions**: Specific exception types for different error categories

### Monitoring Tools

1. **Built-in CLI**: Use the CLI tool for basic monitoring
2. **Flower**: Web-based monitoring (optional)
3. **RabbitMQ Management**: Queue monitoring at http://localhost:15672
4. **Redis CLI**: Result backend monitoring

## Performance Optimization

### Scaling Workers

```bash
# Scale workers horizontally
docker-compose up --scale celery-worker=3

# Or start multiple worker processes
celery -A app.celery_app worker --concurrency=8
```

### Queue Management

- Use specific queues for different task types
- Monitor queue lengths to identify bottlenecks
- Adjust worker allocation based on workload

### Memory Management

- Workers restart after processing 1000 tasks to prevent memory leaks
- Large documents are processed in chunks
- Results are cached in Redis with TTL

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```bash
   # Check RabbitMQ status
   docker-compose ps rabbitmq
   
   # Check Redis status
   docker-compose ps redis
   ```

2. **Task Failures**
   ```bash
   # Check worker logs
   docker-compose logs celery-worker
   
   # Check specific task status
   python -m app.celery_app.cli status --task-id <task-id>
   ```

3. **Performance Issues**
   ```bash
   # Check worker statistics
   python -m app.celery_app.cli workers
   
   # Check queue lengths
   python -m app.celery_app.cli queue-length
   ```

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export CELERY_LOG_LEVEL=DEBUG
export LOG_LEVEL=DEBUG
```

## Testing

Run the test suite:

```bash
# Unit tests
pytest tests/test_celery_tasks.py -v

# Integration tests (requires running services)
pytest tests/test_celery_tasks.py::TestCeleryIntegration -v
```

## Security Considerations

- **Message Encryption**: Consider enabling message encryption for sensitive data
- **Access Control**: RabbitMQ and Redis should be properly secured
- **Input Validation**: All task inputs are validated before processing
- **Resource Limits**: Tasks have time and memory limits to prevent abuse

## Development

### Adding New Tasks

1. Create task function in appropriate module
2. Add task routing configuration in `celery.py`
3. Add tests in `test_celery_tasks.py`
4. Update CLI if needed
5. Document the new task type

### Task Best Practices

- Use descriptive task names
- Include progress tracking for long-running tasks
- Handle errors gracefully with proper logging
- Use appropriate queue for task type
- Include comprehensive tests

## Production Deployment

### Recommended Setup

- Use separate worker nodes for different queue types
- Monitor with Flower or similar tools
- Set up alerting for failed tasks
- Use Redis Cluster for high availability
- Configure RabbitMQ clustering

### Scaling Guidelines

- Start with 1-2 workers per CPU core
- Monitor queue lengths and adjust worker count
- Use dedicated workers for CPU-intensive AI tasks
- Scale horizontally rather than vertically when possible