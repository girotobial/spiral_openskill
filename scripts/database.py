from __future__ import annotations

import datetime
from typing import Any

from common import MatchRow
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
    case,
    create_engine,
    func,
    insert,
    select,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import declarative_base, mapped_column, relationship, sessionmaker

Base = declarative_base()

team_member = Table(
    "team_member",
    Base.metadata,
    Column("player_id", ForeignKey("player.id"), primary_key=True),
    Column("team_id", ForeignKey("team.id"), primary_key=True),
)


class AsDictMixin:
    def as_dict(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class Player(Base, AsDictMixin):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    teams: Mapped[list[Team]] = relationship(
        secondary=team_member,
        back_populates="members",
    )


class Result(Base):
    __tablename__ = "result"

    team_id = Column(ForeignKey("team.id"), primary_key=True)
    match_id = Column(ForeignKey("match.id"), primary_key=True)
    winner: Mapped[bool] = mapped_column(Boolean)
    match: Mapped[Match] = relationship("Match", back_populates="teams")
    team: Mapped[Team] = relationship("Team", back_populates="matches")


class Team(Base, AsDictMixin):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    members: Mapped[list[Player]] = relationship(
        secondary=team_member,
        back_populates="teams",
    )
    matches: Mapped[list[Result]] = relationship(Result, back_populates="team")


class Match(Base):
    __tablename__ = "match"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("session.id"))
    session_index: Mapped[int] = mapped_column(Integer, nullable=False)
    winner_score: Mapped[int] = mapped_column(Integer, nullable=False)
    loser_score: Mapped[int] = mapped_column(Integer, nullable=False)
    margin: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped[Session] = relationship("Session", back_populates="matches")
    teams: Mapped[list[Result]] = relationship(Result, back_populates="match")


class Session(Base):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    club_id: Mapped[int] = mapped_column(ForeignKey("club.id"))

    matches: Mapped[list[Match]] = relationship("Match", back_populates="session")
    club: Mapped[Club] = relationship("Club", back_populates="sessions")

    __table_args__ = (UniqueConstraint("date", "club_id", name="unique_club_session"),)


class Club(Base, AsDictMixin):
    __tablename__ = "club"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    sessions: Mapped[list[Session]] = relationship(Session, back_populates="club")


class SessionRepo:
    def __init__(self, db: Database):
        self.session = db.session
        self.db = db

    def create(self, date: datetime.date) -> Session:
        session = Session(date=date)
        self.session.add(session)
        return session

    def get(self, date: datetime.date, club_id: int) -> Session | None:
        query = (
            select(Session)
            .where(Session.date == date)
            .where(Session.club_id == club_id)
        )
        return self.session.scalars(query).one_or_none()


class PlayerRepo:
    def __init__(self, db: Database):
        self.session = db.session
        self.db = db

    def get(self, name: str) -> Player | None:
        return self.session.scalars(
            select(Player).where(Player.name == name)
        ).one_or_none()

    def get_or_create(self, name: str) -> Player:
        player = self.get(name)
        if player is None:
            player = Player(name=name)
            self.session.add(player)
        return player


class TeamRepo:
    def __init__(self, db: Database):
        self.session = db.session
        self.db = db

    def get(self, players: list[Player]) -> Team | None:
        target_ids = [player.id for player in players]
        num_players = len(target_ids)
        team_subquery = (
            select(team_member.c.team_id)
            .group_by(team_member.c.team_id)
            .having(
                func.sum(case((team_member.c.player_id.in_(target_ids), 1), else_=0))
                == num_players
            )
        ).subquery()
        return self.session.scalars(
            select(Team).join(team_subquery, Team.id == team_subquery.c.team_id)
        ).one_or_none()

    def get_or_create(self, players: list[Player]) -> Team:
        team = self.get(players)
        if team is None:
            team = Team(members=players)
            self.session.add(team)
        return team


class ClubRepo:
    def __init__(self, db: Database):
        self.session = db.session
        self.db = db

    def insert(self, name: str) -> Club:
        self.session.execute(insert(Club), [{"name": name}])
        return self.session.scalars(select(Club).where(Club.name == name)).first()

    def get(self, name: str) -> Club | None:
        return self.session.scalars(select(Club).where(Club.name == name)).one_or_none()

    def get_or_create(self, name: str) -> Club:
        club = self.get(name)
        if club is None:
            club = Club(name=name)
            self.session.add(club)
        return club


class Database:
    session: DatabaseSession
    sessions: SessionRepo
    players: PlayerRepo
    clubs: ClubRepo
    teams: TeamRepo

    def __init__(self, path: str):
        engine = create_engine(f"sqlite:///{path}", echo=True)
        self.session_factory = sessionmaker(engine)

    def __enter__(self) -> Database:
        self.session = self.session_factory()
        self.sessions = SessionRepo(self)
        self.clubs = ClubRepo(self)
        self.players = PlayerRepo(self)
        self.teams = TeamRepo(self)
        return self

    def __exit__(self, *args, **kwargs):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
