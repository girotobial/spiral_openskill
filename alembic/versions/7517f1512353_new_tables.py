"""New tables

Revision ID: 7517f1512353
Revises: 
Create Date: 2025-04-17 18:30:05.153084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7517f1512353'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=True),
    sa.Column('session_index', sa.Integer(), nullable=False),
    sa.Column('winner_score', sa.Integer(), nullable=False),
    sa.Column('loser_score', sa.Integer(), nullable=False),
    sa.Column('margin', sa.Integer(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('winner', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_member',
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['player_id'], ['player.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], ),
    sa.PrimaryKeyConstraint('player_id', 'team_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team_member')
    op.drop_table('team')
    op.drop_table('match')
    op.drop_table('session')
    op.drop_table('player')
    # ### end Alembic commands ###
