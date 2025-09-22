from __future__ import annotations

import datetime
from typing import Any

try:
    from common import Type, MatchRow
except ModuleNotFoundError:
    from .common import Type

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
from sqlalchemy.sql import text

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
    person_id: Mapped[int] = mapped_column(
        ForeignKey("person.id", name="person_id_fkey"), nullable=True
    )

    teams: Mapped[list[Team]] = relationship(
        secondary=team_member,
        back_populates="members",
    )
    person: Mapped[Player] = relationship("Person", back_populates="players")
    rank_history: Mapped[list[RankHistory]] = relationship(
        "RankHistory", back_populates="player"
    )

class RankHistory(Base):
    __tablename__ = "rank_history"

    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"), primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("match.id"), primary_key=True)
    mu: Mapped[int] = mapped_column(nullable=False)
    sigma: Mapped[int] = mapped_column(nullable=False)

    player: Mapped[Player] = relationship(Player, back_populates="rank_history")
    match: Mapped[Match] = relationship("Match")


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
    type_: Mapped[Type] = mapped_column(
        name="type", default=Type.UNDEFINED, nullable=False
    )

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


class Person(Base):
    __tablename__ = "person"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    players: Mapped[list[Player]] = relationship(Player, back_populates="person")


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

    def get_by_id(self, id_: int) -> Player | None:
        return self.session.scalars(
            select(Player).where(Player.id == id_)
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


class PersonRepo:
    def __init__(self, db: Database):
        self.session = db.session

    def get(self, name: str) -> Person | None:
        return self.session.scalars(
            select(Person).where(Person.name == name)
        ).one_or_none()

    def get_or_create(self, name: str) -> Person:
        person = self.get(name)
        if person is None:
            person = Person(name=name)
            self.session.add(person)
        return person


class ViewsRepo:
    def __init__(self, db: Database):
        self.session = db.session

    def matches(self, club_name: str | None = None) -> list[MatchRow]:
        if club_name is None:
            result = self.session.execute(
                text(
                    r"""
                    SELECT 
                        club_name,
                        "date",
                        "type",
                        winner_a,
                        winner_b,
                        winner_score,
                        loser_a,
                        loser_b,
                        loser_score,
                        duration,
                        session_index
                    FROM match_history
                """
                )
            ).all()
        else:
            result = self.session.execute(
                text(
                    r"""
                    SELECT 
                        club_name,
                        "date",
                        "type",
                        winner_a,
                        winner_b,
                        winner_score,
                        loser_a,
                        loser_b,
                        loser_score,
                        duration,
                        session_index
                    FROM match_history
                    WHERE club_name = :club_name
                """
                ),
                {club_name: club_name},
            ).all()
        return [
            MatchRow(
                club=row[0],
                date=row[1],
                type_=row[2],
                winner_a=row[3],
                winner_b=row[4],
                winner_score=row[5],
                loser_a=row[6],
                loser_b=row[7],
                loser_score=row[8],
                duration=row[9],
                session_index=row[10],
            )
            for row in result
        ]


class Database:
    session: DatabaseSession
    sessions: SessionRepo
    players: PlayerRepo
    clubs: ClubRepo
    teams: TeamRepo
    views: ViewsRepo
    people: PersonRepo

    def __init__(self, path: str, echo: bool = False):
        engine = create_engine(f"sqlite:///{path}", echo=echo)
        self.session_factory = sessionmaker(engine)

    def __enter__(self) -> Database:
        self.session = self.session_factory()
        self.sessions = SessionRepo(self)
        self.clubs = ClubRepo(self)
        self.players = PlayerRepo(self)
        self.teams = TeamRepo(self)
        self.views = ViewsRepo(self)
        self.people = PersonRepo(self)
        return self

    def __exit__(self, *args, **kwargs):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
