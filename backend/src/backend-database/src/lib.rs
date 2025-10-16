use chrono::{NaiveDate, NaiveTime};
use sqlx::{SqlitePool, sqlite::SqlitePoolOptions};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DbError {
    #[error(transparent)]
    Sqlx(#[from] sqlx::Error),

    // Keep around in case you want to bubble up domain not-founds from the DB layer
    #[error("row not found")]
    NotFound,
}

#[derive(Clone)]
pub struct Database {
    pool: SqlitePool,
}

impl Database {
    /// Create a connection *pool* to the SQLite file at `path`.
    pub async fn connect(path: &str, _echo: bool) -> Result<Self, DbError> {
        let url = format!("sqlite://{}", path);
        let pool = SqlitePoolOptions::new()
            .max_connections(5)
            .connect(&url)
            .await?;
        Ok(Self { pool })
    }

    /// If you want a "factory" clone per request.
    pub fn clone_for_request(&self) -> Self {
        Self {
            pool: self.pool.clone(),
        }
    }

    // ─────────────────────────────
    // PEOPLE (PersonRepo.get_all)
    // ─────────────────────────────
    pub async fn people_get_all(&self) -> Result<Vec<PersonRow>, DbError> {
        let rows = sqlx::query_as!(
            PersonRow,
            r#"
            SELECT id, name
            FROM person
            ORDER BY name ASC
            "#
        )
        .fetch_all(&self.pool)
        .await?;
        Ok(rows)
    }

    // ───────────────────────────────────────────────────────────────
    // VIEWS: detailed_ranking_history(person_id, club_id = 1)
    // ───────────────────────────────────────────────────────────────
    pub async fn view_detailed_ranking_history(
        &self,
        person_id: i32,
        club_id: i32,
    ) -> Result<Vec<DetailedRankingHistoryRow>, DbError> {
        let rows = sqlx::query_as::<_, DetailedRankingHistoryRow>(
            r#"
            SELECT
                match_id,
                date        as "date: _",
                start_time  as "start_time: _",
                winner      as "winner: bool",
                CAST(mu    AS REAL) AS "mu!: f64",
                CAST(sigma AS REAL) AS "sigma!: f64"
            FROM detailed_ranking_history
            WHERE person_id = ?1 AND club_id = ?2
            ORDER BY match_id ASC
            "#,
        )
        .bind(person_id)
        .bind(club_id)
        .fetch_all(&self.pool)
        .await?;
        Ok(rows)
    }

    // ───────────────────────────────────────────────────────────────
    // VIEWS: player_stats(person_id)
    // ───────────────────────────────────────────────────────────────
    pub async fn view_player_stats(
        &self,
        person_id: i32,
    ) -> Result<Option<PlayerStatsRow>, DbError> {
        let row = sqlx::query_as::<_, PlayerStatsRow>(
            r#"
            SELECT
                person_id                               as "person_id!: i32",
                CAST(average_points_difference AS REAL) as "average_points_difference!: f64",
                total_matches                           as "total_matches!: i32",
                wins                                     as "wins!: i32"
            FROM player_stats
            WHERE person_id = ?1
            "#,
        )
        .bind(person_id)
        .fetch_optional(&self.pool)
        .await?;
        Ok(row)
    }

    // ───────────────────────────────────────────────────────────────
    // VIEWS: partner_stats(person_id, club_id)
    // ───────────────────────────────────────────────────────────────
    pub async fn view_partner_stats(
        &self,
        person_id: i32,
        club_id: i32,
    ) -> Result<Vec<OtherPlayerStatsRow>, DbError> {
        let sql = r#"
            WITH target_players AS (
                SELECT id AS player_id
                FROM player
                WHERE person_id = ?1
            ),
            partners AS (
                SELECT tm1.team_id, pl2.person_id AS partner_person_id
                FROM team_member tm1
                JOIN target_players tp
                  ON tp.player_id = tm1.player_id
                JOIN team_member tm2
                  ON tm2.team_id = tm1.team_id
                 AND tm2.player_id <> tm1.player_id
                JOIN player pl2
                  ON pl2.id = tm2.player_id
                GROUP BY tm1.team_id, pl2.person_id
            ),
            club_matches AS (
                SELECT r.team_id, r.match_id, r.winner
                FROM result r
                JOIN match m   ON m.id = r.match_id
                JOIN session s ON s.id = m.session_id
                WHERE (s.club_id = ?2 OR s.club_id IS NULL)
            ),
            partner_stats AS (
                SELECT
                    p.partner_person_id,
                    COUNT(DISTINCT cm.match_id) AS matches_together,
                    SUM(cm.winner) AS wins_together
                FROM partners p
                JOIN club_matches cm ON cm.team_id = p.team_id
                GROUP BY p.partner_person_id
            )
            SELECT
                ps.partner_person_id AS player_id,
                per.name AS player_name,
                ps.wins_together AS wins,
                ps.matches_together AS matches,
                ROUND(CAST(ps.wins_together AS FLOAT) / NULLIF(ps.matches_together, 0), 3) AS win_rate
            FROM partner_stats ps
            JOIN person per ON per.id = ps.partner_person_id
            ORDER BY matches DESC
        "#;

        let rows = sqlx::query_as::<_, OtherPlayerStatsRow>(sql)
            .bind(person_id)
            .bind(club_id)
            .fetch_all(&self.pool)
            .await?;
        Ok(rows)
    }

    // ───────────────────────────────────────────────────────────────
    // VIEWS: opponent_stats(person_id, club_id)
    // ───────────────────────────────────────────────────────────────
    pub async fn view_opponent_stats(
        &self,
        person_id: i32,
        club_id: i32,
    ) -> Result<Vec<OtherPlayerStatsRow>, DbError> {
        let sql = r#"
            WITH target_players AS (
                SELECT id AS player_id
                FROM player
                WHERE person_id = ?1
            ),
            club_match_ids AS (
                SELECT m.id AS match_id
                FROM match m
                JOIN session s ON s.id = m.session_id
                WHERE s.club_id = ?2
            ),
            target_team_matches AS (
                SELECT DISTINCT
                    r.match_id,
                    r.team_id       AS target_team_id,
                    r.winner        AS target_won
                FROM result r
                JOIN team_member tm   ON tm.team_id = r.team_id
                JOIN target_players tp ON tp.player_id = tm.player_id
                WHERE r.match_id IN (SELECT match_id FROM club_match_ids)
            ),
            opponents AS (
                SELECT DISTINCT
                    ttm.match_id,
                    tm2.player_id   AS opponent_player_id,
                    ttm.target_won
                FROM target_team_matches ttm
                JOIN result r2       ON r2.match_id = ttm.match_id
                                     AND r2.team_id <> ttm.target_team_id
                JOIN team_member tm2 ON tm2.team_id = r2.team_id
            ),
            opponent_stats AS (
                SELECT
                    pl2.person_id AS opponent_person_id,
                    COUNT(DISTINCT o.match_id) AS matches_vs,
                    SUM(CASE WHEN o.target_won = 1 THEN 1 ELSE 0 END) AS wins_vs
                FROM opponents o
                JOIN player pl2 ON pl2.id = o.opponent_player_id
                GROUP BY pl2.person_id
            )
            SELECT
                os.opponent_person_id AS player_id,
                per.name AS player_name,
                os.wins_vs AS wins,
                os.matches_vs AS matches,
                ROUND(CAST(os.wins_vs AS FLOAT) / NULLIF(os.matches_vs, 0), 3) AS win_rate
            FROM opponent_stats os
            JOIN person per ON per.id = os.opponent_person_id
            ORDER BY matches DESC
        "#;

        let rows = sqlx::query_as::<_, OtherPlayerStatsRow>(sql)
            .bind(person_id)
            .bind(club_id)
            .fetch_all(&self.pool)
            .await?;
        Ok(rows)
    }
}

// Rows analogous to your Python-side DB results
#[derive(Clone, Debug, sqlx::FromRow)]
pub struct PersonRow {
    pub id: i64,
    pub name: String,
}

#[derive(Clone, Debug, sqlx::FromRow)]
pub struct DetailedRankingHistoryRow {
    pub match_id: i64,
    pub date: NaiveDate,
    pub start_time: NaiveTime,
    pub mu: f64,
    pub sigma: f64,
    pub winner: bool,
}

#[derive(Clone, Debug, sqlx::FromRow)]
pub struct PlayerStatsRow {
    pub person_id: i64,
    pub average_points_difference: f64,
    pub total_matches: i64,
    pub wins: i64,
}

#[derive(Clone, Debug, sqlx::FromRow)]
pub struct OtherPlayerStatsRow {
    pub player_id: i64,
    pub player_name: String,
    pub wins: i64,
    pub matches: i64,
    pub win_rate: f64,
}
