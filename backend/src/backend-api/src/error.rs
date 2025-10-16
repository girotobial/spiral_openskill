use axum::{http::StatusCode, response::IntoResponse};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("not found")]
    NotFound,
    #[error("internal error")]
    Internal,
}

impl IntoResponse for AppError {
    fn into_response(self) -> axum::response::Response {
        let response = match self {
            Self::Internal => (StatusCode::INTERNAL_SERVER_ERROR, "Internal Server Error"),
            Self::NotFound => (StatusCode::NOT_FOUND, "Not Found"),
        };
        response.into_response()
    }
}

impl From<backend_database::DbError> for AppError {
    fn from(value: backend_database::DbError) -> Self {
        match value {
            backend_database::DbError::NotFound => Self::NotFound,
            backend_database::DbError::Sqlx(_) => Self::Internal,
        }
    }
}
