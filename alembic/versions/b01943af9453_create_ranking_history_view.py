"""create ranking_history view

Revision ID: b01943af9453
Revises: ea576ea0ccbf
Create Date: 2025-10-04 23:02:00.959649

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b01943af9453"
down_revision: Union[str, None] = "ea576ea0ccbf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

VIEW_SQL = """
    CREATE VIEW IF NOT EXISTS detailed_ranking_history AS
        SELECT p.person_id, r.match_id, s.date, m.start_time, r.winner, rh.mu, rh.sigma
        FROM "result" r
        INNER JOIN team t
            ON t.id = r.team_id
        INNER JOIN team_member tm
            ON t.id = tm.team_id
        INNER JOIN rank_history rh
            ON rh.player_id = tm.player_id AND rh.match_id = r.match_id
        INNER JOIN "match" m
            ON m.id = r.match_id
        INNER JOIN "session" s
            ON m.session_id = s.id
        INNER JOIN player p
            ON rh.player_id = p.id
        ORDER BY s.date, m.start_time ASC
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text(VIEW_SQL))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS detailed_ranking_history")
