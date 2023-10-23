"""update

Revision ID: 9421071a6c0c
Revises: 33bca5f54357
Create Date: 2023-10-23 14:29:01.623780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9421071a6c0c'
down_revision = '33bca5f54357'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_task')
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deadline', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('project_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('status_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_task_project', 'project', ['project_id'], ['project_id'])
        batch_op.create_foreign_key('fk_task_status', 'status', ['status_id'], ['status_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint('fk_task_status', type_='foreignkey')
        batch_op.drop_constraint('fk_task_project', type_='foreignkey')
        batch_op.drop_column('status_id')
        batch_op.drop_column('project_id')
        batch_op.drop_column('deadline')

    op.create_table('_alembic_tmp_task',
    sa.Column('task_id', sa.INTEGER(), nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), nullable=False),
    sa.Column('priority_id', sa.INTEGER(), nullable=True),
    sa.Column('isCompleted', sa.BOOLEAN(), nullable=True),
    sa.Column('deadline', sa.DATETIME(), nullable=False),
    sa.Column('project_id', sa.INTEGER(), nullable=True),
    sa.Column('status_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['priority_id'], ['priority.priority_id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.project_id'], name='fk_task_project'),
    sa.ForeignKeyConstraint(['status_id'], ['status.status_id'], name='fk_task_status'),
    sa.PrimaryKeyConstraint('task_id')
    )
    # ### end Alembic commands ###