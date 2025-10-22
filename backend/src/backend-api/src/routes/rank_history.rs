use crate::AppState;
use crate::error::AppError;
use axum::extract::{Path, State};
use axum::response::Json;
use chrono::{NaiveDate, NaiveDateTime, NaiveTime};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct RankHistoryEntry {
    match_id: i64,
    date: NaiveDate,
    start_time: NaiveTime,
    datetime: NaiveDateTime,
    winner: bool,
    mu: f64,
    sigma: f64,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct RankHistory {
    player_id: i32,
    history: Vec<RankHistoryEntry>,
}

#[tracing::instrument]
pub async fn get_rank_history(
    Path(player_id): Path<i32>,
    State(state): State<AppState>,
) -> Result<Json<RankHistory>, AppError> {
    tracing::info!("{}", player_id);
    let db = state.database;

    let history_rows = db
        .view_detailed_ranking_history(player_id, 1)
        .await
        .map_err(|e| {
            tracing::error!("DB ERROR {e:?}");
            AppError::from(e)
        })?;

    let initial_dt = NaiveDateTime::new(
        NaiveDate::from_ymd_opt(2025, 1, 1).unwrap(),
        NaiveTime::from_hms_opt(0, 0, 0).unwrap(),
    );

    let initial = RankHistoryEntry {
        match_id: 0,
        date: initial_dt.date(),
        start_time: initial_dt.time(),
        datetime: initial_dt,
        mu: 25.0,
        sigma: 25.0 / 3.0,
        winner: false,
    };

    let mut history = Vec::with_capacity(history_rows.len() + 1);
    history.push(initial);

    history.extend(history_rows.into_iter().map(|row| RankHistoryEntry {
        match_id: row.match_id,
        date: row.date,
        start_time: row.start_time,
        datetime: NaiveDateTime::new(row.date, row.start_time),
        mu: row.mu,
        sigma: row.sigma,
        winner: row.winner,
    }));

    Ok(Json(RankHistory { player_id, history }))
}
