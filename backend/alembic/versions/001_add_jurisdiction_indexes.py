"""Add jurisdiction-specific indexes for performance optimization

Revision ID: 001
Revises: 
Create Date: 2024-12-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add jurisdiction-specific indexes for optimal query performance."""
    
    # Document indexes for jurisdiction-aware queries
    op.create_index(
        'idx_documents_jurisdiction_type',
        'documents',
        ['jurisdiction', 'document_type'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_documents_jurisdiction_status',
        'documents',
        ['jurisdiction', 'analysis_status'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_documents_user_jurisdiction',
        'documents',
        ['uploaded_by', 'jurisdiction'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # GIN index for detected_jurisdiction JSON field
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_detected_jurisdiction_gin 
        ON documents USING GIN (detected_jurisdiction)
    """)
    
    # Full-text search index for document content
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_content_fts 
        ON documents USING GIN (to_tsvector('english', content))
    """)
    
    # Analysis results indexes
    op.create_index(
        'idx_analysis_document_status',
        'analysis_results',
        ['document_id', 'status'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # GIN indexes for JSON fields in analysis results
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_summary_gin 
        ON analysis_results USING GIN (summary)
    """)
    
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_risks_gin 
        ON analysis_results USING GIN (risks)
    """)
    
    # Jurisdiction analysis indexes
    op.create_index(
        'idx_jurisdiction_analysis_doc_jurisdiction',
        'jurisdiction_analysis',
        ['document_id', 'jurisdiction'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    op.create_index(
        'idx_jurisdiction_analysis_jurisdiction_confidence',
        'jurisdiction_analysis',
        ['jurisdiction', 'confidence_score'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # GIN index for analysis results JSON
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jurisdiction_analysis_results_gin 
        ON jurisdiction_analysis USING GIN (analysis_results)
    """)
    
    # User indexes for performance
    op.create_index(
        'idx_users_role_active',
        'users',
        ['role', 'is_active'],
        postgresql_concurrently=True,
        if_not_exists=True
    )
    
    # Partial index for organization queries (only non-null values)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_organization 
        ON users (organization) WHERE organization IS NOT NULL
    """)


def downgrade() -> None:
    """Remove jurisdiction-specific indexes."""
    
    # Drop all the indexes created in upgrade
    indexes_to_drop = [
        'idx_documents_jurisdiction_type',
        'idx_documents_jurisdiction_status', 
        'idx_documents_user_jurisdiction',
        'idx_documents_detected_jurisdiction_gin',
        'idx_documents_content_fts',
        'idx_analysis_document_status',
        'idx_analysis_summary_gin',
        'idx_analysis_risks_gin',
        'idx_jurisdiction_analysis_doc_jurisdiction',
        'idx_jurisdiction_analysis_jurisdiction_confidence',
        'idx_jurisdiction_analysis_results_gin',
        'idx_users_role_active',
        'idx_users_organization'
    ]
    
    for index_name in indexes_to_drop:
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {index_name}")