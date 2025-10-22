use backend_database::Database;

#[derive(Clone, Debug)]
pub struct AppState {
    pub database: Database,
}
