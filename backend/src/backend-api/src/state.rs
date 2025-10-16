use backend_database::Database;

#[derive(Clone)]
pub struct AppState {
    pub database: Database,
}
