from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    teams = relationship("TeamMember", back_populates="player")


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("match.id"))
    winner = Column(Boolean)
    members = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    match = relationship("Match", back_populates="teams")


class TeamMember(Base):
    __tablename__ = "team_member"

    player_id = Column(Integer, ForeignKey("player.id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("team.id"), primary_key=True)

    team = relationship("Team", back_populates="member")
    player = relationship("Player", back_populates="teams")


class Match(Base):
    __tablename__ = "match"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("session.id"))
    session_index = Column(Integer, nullable=False)
    winner_score = Column(Integer, nullable=False)
    loser_score = Column(Integer, nullable=False)
    margin = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)

    session = relationship("Session", back_populates="matches")
    teams = relationship("Team", back_populates="match")


class Session(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)

    matches = relationship("Match", back_populates="session")


class Database:
    def __init__(self, path: str):
        engine = create_engine(f"sqlite:///{path}")
        self.session = DatabaseSession(engine)
