"""
Initial migration for Tracerfy Backend
Creates all necessary tables for the skip tracing platform
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema"""
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    
    # Create credits table
    op.create_table('credits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Integer(), nullable=False, default=0),
        sa.Column('total_purchased', sa.Integer(), nullable=False, default=0),
        sa.Column('total_used', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_credits_user_id'), 'credits', ['user_id'], unique=True)
    
    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'])
    
    # Create files table
    op.create_table('files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='uploaded'),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('processed_records', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_user_id'), 'files', ['user_id'])
    
    # Create records table
    op.create_table('records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=False),
        sa.Column('row_number', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.Column('county', sa.String(length=100), nullable=True),
        sa.Column('property_type', sa.String(length=50), nullable=True),
        sa.Column('assessed_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('last_sale_date', sa.Date(), nullable=True),
        sa.Column('last_sale_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_records_file_id'), 'records', ['file_id'])
    
    # Create trace_results table
    op.create_table('trace_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('phones', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('emails', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.Integer(), nullable=True),
        sa.Column('data_sources', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['record_id'], ['records.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trace_results_record_id'), 'trace_results', ['record_id'])
    
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('priority', sa.Integer(), nullable=False, default=5),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('processed_records', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_records', sa.Integer(), nullable=False, default=0),
        sa.Column('credits_used', sa.Integer(), nullable=False, default=0),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_file_id'), 'jobs', ['file_id'])
    op.create_index(op.f('ix_jobs_user_id'), 'jobs', ['user_id'])
    
    # Create dnc table
    op.create_table('dnc',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('original_phone', sa.String(length=20), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('campaign', sa.String(length=100), nullable=True),
        sa.Column('federal_dnc', sa.Boolean(), nullable=False, default=False),
        sa.Column('state_dnc', sa.Boolean(), nullable=False, default=False),
        sa.Column('dma_dnc', sa.Boolean(), nullable=False, default=False),
        sa.Column('tcpa_litigator', sa.Boolean(), nullable=False, default=False),
        sa.Column('clean', sa.Boolean(), nullable=False, default=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('scrub_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dnc_file_id'), 'dnc', ['file_id'])
    op.create_index(op.f('ix_dnc_phone'), 'dnc', ['phone'])
    op.create_index(op.f('ix_dnc_user_id'), 'dnc', ['user_id'])
    
    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, default=0),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_key'), 'api_keys', ['key'], unique=True)
    op.create_index(op.f('ix_api_keys_user_id'), 'api_keys', ['user_id'])
    
    # Create webhooks table
    op.create_table('webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('events', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('secret', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_triggered', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trigger_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhooks_user_id'), 'webhooks', ['user_id'])
    
    # Create county_lead_types table
    op.create_table('county_lead_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_per_record', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_county_lead_types_name'), 'county_lead_types', ['name'], unique=True)
    
    # Create county_leads table
    op.create_table('county_leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('county_lead_type_id', sa.Integer(), nullable=False),
        sa.Column('county', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('total_records', sa.Integer(), nullable=False),
        sa.Column('price_per_record', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('download_url', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['county_lead_type_id'], ['county_lead_types.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_county_leads_county_lead_type_id'), 'county_leads', ['county_lead_type_id'])
    op.create_index(op.f('ix_county_leads_user_id'), 'county_leads', ['user_id'])
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('email_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_county_leads_user_id'), table_name='county_leads')
    op.drop_index(op.f('ix_county_leads_county_lead_type_id'), table_name='county_leads')
    op.drop_table('county_leads')
    op.drop_index(op.f('ix_county_lead_types_name'), table_name='county_lead_types')
    op.drop_table('county_lead_types')
    op.drop_index(op.f('ix_webhooks_user_id'), table_name='webhooks')
    op.drop_table('webhooks')
    op.drop_index(op.f('ix_api_keys_user_id'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_key'), table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_index(op.f('ix_dnc_user_id'), table_name='dnc')
    op.drop_index(op.f('ix_dnc_phone'), table_name='dnc')
    op.drop_index(op.f('ix_dnc_file_id'), table_name='dnc')
    op.drop_table('dnc')
    op.drop_index(op.f('ix_jobs_user_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_file_id'), table_name='jobs')
    op.drop_table('jobs')
    op.drop_index(op.f('ix_trace_results_record_id'), table_name='trace_results')
    op.drop_table('trace_results')
    op.drop_index(op.f('ix_records_file_id'), table_name='records')
    op.drop_table('records')
    op.drop_index(op.f('ix_files_user_id'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_credits_user_id'), table_name='credits')
    op.drop_table('credits')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
