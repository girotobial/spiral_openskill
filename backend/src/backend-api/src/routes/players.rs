use crate::{error::AppError, state::AppState};
use axum::{extract::State, response::Json};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Player {
    id: i64,
    name: String,
}

pub async fn get_players(State(state): State<AppState>) -> Result<Json<Vec<Player>>, AppError> {
    let db = &state.database;

    let players = db
        .people_get_all()
        .await?
        .into_iter()
        .map(|r| Player {
            id: r.id,
            name: r.name,
        })
        .collect();

    Ok(Json(players))
}
