use backend_api::Api;
use backend_database::Database;
use dotenvy::dotenv;
use tracing::{Level, info};
use tracing_subscriber::EnvFilter;

#[tokio::main]
async fn main() {
    dotenv().ok();

    // Load env similar to your Python code
    let db_path = std::env::var("DB_PATH").unwrap_or_else(|_| "data.db".to_string());
    let db_echo = std::env::var("DB_ECHO")
        .ok()
        .and_then(|v| v.parse::<bool>().ok())
        .unwrap_or(false);

    // Logging
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| EnvFilter::new("info,axum=info,tower_http=info")),
        )
        .with_max_level(Level::DEBUG)
        .init();

    info!("Connecting to {}", &db_path);
    let database = Database::connect(&db_path, db_echo).await.unwrap();
    Api::new(database).serve().await
}
