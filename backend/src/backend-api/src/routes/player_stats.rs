use axum::extract::{Path, State};
use axum::response::Json;
use backend_database::PlayerStatsRow;
use serde::{Deserialize, Serialize};

use crate::{AppState, error::AppError};

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct PlayerStats {
    player_id: i64,
    average_points_difference: f64,
    total_matches: i64,
    wins: i64,
}

impl From<PlayerStatsRow> for PlayerStats {
    fn from(value: PlayerStatsRow) -> Self {
        Self {
            player_id: value.person_id,
            average_points_difference: value.average_points_difference,
            total_matches: value.total_matches,
            wins: value.wins,
        }
    }
}

pub async fn get_player_stats(
    Path(player_id): Path<i32>,
    State(state): State<AppState>,
) -> Result<Json<PlayerStats>, AppError> {
    let db = state.database;

    let stats = db.view_player_stats(player_id).await.map_err(|e| {
        tracing::error!("DB ERROR {e:?}");
        AppError::from(e)
    })?;

    Ok(Json(
        stats.map(PlayerStats::from).ok_or(AppError::NotFound)?,
    ))
}
