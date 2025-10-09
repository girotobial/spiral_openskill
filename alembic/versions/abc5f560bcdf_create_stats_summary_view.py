"""create stats summary view

Revision ID: abc5f560bcdf
Revises: b01943af9453
Create Date: 2025-10-09 11:50:58.664269

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abc5f560bcdf"
down_revision: Union[str, None] = "b01943af9453"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SQL_TEXT = """
CREATE VIEW IF NOT EXISTS player_stats AS
WITH margin_correction AS (
	SELECT player.person_id, "match".id, "result".winner, CASE WHEN "result".winner THEN "match".margin ELSE "match".margin * -1 END margin
	FROM "match"
	INNER JOIN "session"
		ON "session".id = "match".session_id
	INNER JOIN "result"
		ON "result".match_id = "match".id
	INNER JOIN "team"
		ON "team".id = "result".team_id
	INNER JOIN "team_member"
		ON "team_member".team_id = team.id
	INNER JOIN "player"
		ON "player".id = "team_member".player_id
	WHERE "session".club_id = 1
)

    SELECT person_id, AVG(margin) AS "average_points_difference", COUNT(id) AS total_matches, SUM(winner) AS wins
    FROM margin_correction
    GROUP BY person_id
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(SQL_TEXT)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS player_stats")
