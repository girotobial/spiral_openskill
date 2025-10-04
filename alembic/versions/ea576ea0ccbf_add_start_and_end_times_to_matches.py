"""add start and end times to matches

Revision ID: ea576ea0ccbf
Revises: e8aadd4e5967
Create Date: 2025-10-03 12:03:45.814458

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea576ea0ccbf"
down_revision: Union[str, None] = "e8aadd4e5967"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_match_history_view(old: bool = False) -> None:
    """Upgrade schema."""
    SQLTEXTNEW = """
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
            m.duration,
            m.start_time,
            m.end_time
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
        cm.session_index,
        cm.start_time,
        cm.end_time
    FROM club_matches cm
    INNER JOIN winners w
        ON w.match_id = cm.id
    INNER JOIN losers l
        ON l.match_id = cm.id
    """
    SQLTEXTOLD = """
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

    sqltext = SQLTEXTOLD if old else SQLTEXTNEW

    op.execute(f"CREATE VIEW IF NOT EXISTS match_history AS {sqltext}")


def _drop_view_if_exists(conn, view_name: str) -> bool:
    insp = sa.inspect(conn)
    views = set(insp.get_view_names())
    if view_name in views:
        op.execute(sa.text(f'DROP VIEW IF EXISTS"{view_name}"'))
        return True
    return False


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###

    conn = op.get_bind()
    _drop_view_if_exists(conn, "match_history")

    with op.batch_alter_table("match", schema=None) as batch_op:
        batch_op.add_column(sa.Column("start_time", sa.Time(), nullable=True))
        batch_op.add_column(sa.Column("end_time", sa.Time(), nullable=True))

    op.execute(
        sa.text(
            """
                UPDATE match
                SET start_time = '00:00:00',
                    end_time = '00:00:00'
            """
        )
    )

    with op.batch_alter_table("match", schema=None) as batch_op:
        batch_op.alter_column("start_time", nullable=False)
        batch_op.alter_column("end_time", nullable=False)

    create_match_history_view()

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    _drop_view_if_exists(conn, "match_history")
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("match", schema=None) as batch_op:
        batch_op.drop_column("end_time")
        batch_op.drop_column("start_time")

    create_match_history_view(old=True)

    # ### end Alembic commands ###
