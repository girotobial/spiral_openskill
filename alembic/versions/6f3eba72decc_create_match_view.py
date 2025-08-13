"""Create Match view

Revision ID: 6f3eba72decc
Revises: 062865ebee50
Create Date: 2025-08-13 13:23:03.089547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f3eba72decc'
down_revision: Union[str, None] = '062865ebee50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SQLTEXT = """
    WITH player_names as (
	SELECT p.id, pe.name
	FROM player p
	INNER JOIN person pe
		ON p.person_id = pe.id
),

team_players as (
	SELECT 
		tm.team_id, tm.player_id as "player_1_id", 
		tm2.player_id as "player_2_id"
	FROM team_member tm
	INNER JOIN team_member tm2 
		ON tm.team_id = tm2.team_id 
		AND tm.player_id < tm2.player_id
),

team_names as (
	SELECT 
		tp.team_id, 
		pe1.name as player_1, 
		pe2.name as player_2
	FROM team_players tp
	INNER JOIN player_names pe1 
		ON tp.player_1_id = pe1.id
	INNER JOIN player_names pe2
		ON tp.player_2_id = pe2.id	
),

club_matches as (
	SELECT
		m.id,
		c.name as club_name,
		s."date",
		m."type",
		m.session_index,
		m.winner_score,
		m.loser_score,
		m.margin,
		m.duration
	FROM club c
	INNER JOIN "session" s
		ON s.club_id = c.id
	INNER JOIN "match" m
		ON m.session_id = s.id
	
),

winners as (
	SELECT 
		r.match_id,
		tn.player_1 as winner_a,
		tn.player_2 as winner_b
	FROM "result" r
	INNER JOIN team_names tn
		ON tn.team_id = r.team_id
	WHERE 
		r.winner
),

losers as (
	SELECT 
		r.match_id,
		tn.player_1 as loser_a,
		tn.player_2 as loser_b
	FROM "result" r
	INNER JOIN team_names tn
		ON tn.team_id = r.team_id
	WHERE 
		NOT r.winner
)

SELECT 
	cm.id,
	cm.club_name,
	cm.date,
	cm."type",
	w.winner_a,
	w.winner_b,
	cm.winner_score,
	l.loser_a,
	l.loser_b,
	cm.loser_score,
	(cm.winner_score - cm.loser_score) as margin,
	cm.duration,
	cm.session_index
FROM club_matches cm
INNER JOIN winners w
	ON w.match_id = cm.id
INNER JOIN losers l
	ON l.match_id = cm.id
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        f"CREATE VIEW IF NOT EXISTS match_history AS {SQLTEXT}"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DROP VIEW IF EXISTS match_history;"
    )