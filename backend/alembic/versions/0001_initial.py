"""Create applications and cascading interviews."""
from alembic import op
import sqlalchemy as sa
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('applications',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('company_name', sa.String(160), nullable=False),
        sa.Column('role_title', sa.String(160), nullable=False),
        sa.Column('employment_type', sa.String(20), nullable=False),
        sa.Column('work_mode', sa.String(20), nullable=False),
        sa.Column('stage', sa.String(20), nullable=False),
        sa.Column('location', sa.String(200)), sa.Column('job_url', sa.String(2048)),
        sa.Column('applied_date', sa.Date), sa.Column('deadline', sa.Date), sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("stage IN ('Saved','Applied','Screening','Interview','Offer','Rejected','Withdrawn')", name='application_stage'),
        sa.CheckConstraint("employment_type IN ('Internship','Full-time','Part-time','Contract')", name='employment_type'),
        sa.CheckConstraint("work_mode IN ('Remote','Hybrid','On-site')", name='work_mode'),
        sa.CheckConstraint("length(trim(company_name)) > 0 AND length(trim(role_title)) > 0", name='required_names'))
    for field in ['company_name','role_title','stage','employment_type','deadline','updated_at']:
        op.create_index('ix_applications_'+field, 'applications', [field])
    op.create_table('interviews',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('application_id', sa.Integer, sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('interview_type', sa.String(20), nullable=False), sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("interview_type IN ('Phone','Video','On-site','Assessment')", name='interview_type'))
    for field in ['application_id','scheduled_at']:
        op.create_index('ix_interviews_'+field, 'interviews', [field])

def downgrade():
    op.drop_table('interviews')
    op.drop_table('applications')
