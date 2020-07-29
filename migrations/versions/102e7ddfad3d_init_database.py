"""init database

Revision ID: 102e7ddfad3d
Revises: 
Create Date: 2020-07-28 18:57:26.224706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '102e7ddfad3d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=40), nullable=True),
    sa.Column('email', sa.String(length=80), nullable=True),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('about_me', sa.String(length=300), nullable=True),
    sa.Column('registered_date', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('password_hash')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.id'], )
    )
    op.create_table('notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('org_attachment_filename', sa.String(length=256), nullable=True),
    sa.Column('attachment_hash', sa.String(length=80), nullable=True),
    sa.Column('file_path', sa.String(length=256), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_attachment_hash'), 'notes', ['attachment_hash'], unique=True)
    op.create_index(op.f('ix_notes_description'), 'notes', ['description'], unique=False)
    op.create_index(op.f('ix_notes_file_path'), 'notes', ['file_path'], unique=False)
    op.create_index(op.f('ix_notes_org_attachment_filename'), 'notes', ['org_attachment_filename'], unique=False)
    op.create_index(op.f('ix_notes_timestamp'), 'notes', ['timestamp'], unique=False)
    op.create_index(op.f('ix_notes_title'), 'notes', ['title'], unique=False)
    op.create_table('subscribed_notes',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('note_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscribed_notes')
    op.drop_index(op.f('ix_notes_title'), table_name='notes')
    op.drop_index(op.f('ix_notes_timestamp'), table_name='notes')
    op.drop_index(op.f('ix_notes_org_attachment_filename'), table_name='notes')
    op.drop_index(op.f('ix_notes_file_path'), table_name='notes')
    op.drop_index(op.f('ix_notes_description'), table_name='notes')
    op.drop_index(op.f('ix_notes_attachment_hash'), table_name='notes')
    op.drop_table('notes')
    op.drop_table('followers')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
