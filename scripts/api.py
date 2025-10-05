from contextlib import asynccontextmanager
from datetime import date, datetime, time
from typing import Annotated, Iterator

from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel

from .database import Database

DB_PATH = "sqlite:///../data.db"
DB_ECHO = False


@asynccontextmanager
async def lifespan(_app: FastAPI):
    app.state.db_factory = lambda: Database(DB_PATH, echo=DB_ECHO)
    yield


def get_db(request: Request) -> Iterator[Database]:
    with request.app.state.db_factory() as db:
        yield db


Db = Annotated[Database, Depends(get_db)]


class Player(BaseModel):
    id: int
    name: str


class RankHistoryEntry(BaseModel):
    match_id: int
    date: date
    start_time: time
    datetime: datetime
    winner: bool
    mu: float
    sigma: float


class RankHistory(BaseModel):
    player_id: int
    history: list[RankHistoryEntry]


app = FastAPI(lifespan=lifespan, title="Spiral Openskill")


@app.get("/players", response_model=list[Player])
def get_people(db: Db) -> list[Player]:
    with db:
        players = db.people.get_all()
    return [Player(id=player.id, name=player.name) for player in players]


@app.get("/rank_history/{player_id}", response_model=RankHistory)
def get_rank_history(player_id: int, db: Db) -> RankHistory:
    with db:
        history = db.views.detailed_ranking_history(player_id)
        return RankHistory(
            player_id=player_id,
            history=[
                RankHistoryEntry(
                    match_id=entry.match_id,
                    date=entry.date,
                    start_time=entry.start_time,
                    datetime=datetime.combine(entry.date, entry.start_time),
                    mu=entry.mu,
                    sigma=entry.sigma,
                    winner=entry.winner,
                )
                for entry in history
            ],
        )
