use crate::{routes::get_players, state::AppState};
use axum::{Router, routing::get};
use backend_database::Database;
use std::net::SocketAddr;
use tracing::info;

pub struct Api<State> {
    state: State,
}

impl Api<Database> {
    pub fn new(database: Database) -> Api<AppState> {
        Api {
            state: AppState { database },
        }
    }
}

impl Api<AppState> {
    pub async fn serve(self) {
        let state = self.state;

        let router = Router::new()
            .route("/players", get(get_players))
            .with_state(state);

        let addr: SocketAddr = "0.0.0.0:8000".parse().unwrap();
        info!("Spiral Openskill API listening on http://{addr}");
        axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), router)
            .await
            .unwrap()
    }
}
