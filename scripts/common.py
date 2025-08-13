import datetime
import enum
from dataclasses import dataclass
from typing import Generic, Self, TypeVar

from bs4.element import Tag

T = TypeVar("T")


class SafeList(list, Generic[T]):
    def get(self, index: int) -> T | None:
        try:
            return self[index]
        except IndexError:
            return None


def _extract_name(text: str) -> str:
    return " ".join(s for s in text.strip().split(" ")).strip()


@dataclass
class Player:
    name: str
    ranking: float

    @classmethod
    def from_span(cls, span: Tag) -> Self:
        name = _extract_name(span.contents[0].text)
        ranking = float(span.contents[1].text)
        return cls(name=name, ranking=ranking)


class Type(enum.StrEnum):
    MENS = "Mens"
    MIXED = "Mixed"
    IMBALANCED_MIXED = "Imbalanced Mixed"
    LADIES = "Ladies"
    UNDEFINED = "Undefined"

    @classmethod
    def from_match_type(cls, type_: str) -> "Type":
        match type_:
            case "LMLM" | "MLML":
                return cls.MIXED
            case (
                "LMMM"
                | "MLMM"
                | "MMLM"
                | "MMML"
                | "MLLL"
                | "LMLL"
                | "LLML"
                | "LLLM"
                | "MMLL"
                | "LLMM"
            ):
                return cls.IMBALANCED_MIXED
            case "MMMM":
                return cls.MENS
            case "LLLL":
                return cls.LADIES
        return cls.UNDEFINED


@dataclass
class Match:
    type_: Type
    winners: SafeList[Player]
    losers: SafeList[Player]
    winner_score: int
    loser_score: int
    duration: datetime.timedelta


@dataclass
class MatchRow:
    date: datetime.date
    type_: str
    winner_a: str
    winner_b: str | None
    winner_score: int
    loser_a: str
    loser_b: str | None
    loser_score: int
    duration: datetime.timedelta
    session_index: int

    @classmethod
    def from_match(cls, value: Match, date: datetime.date, session_idx: int) -> Self:
        winner_b = value.winners.get(1)
        if winner_b is not None:
            winner_b_str = winner_b.name
        else:
            winner_b_str = None

        loser_b = value.losers.get(1)
        if loser_b is not None:
            loser_b_str = loser_b.name
        else:
            loser_b_str = None

        return cls(
            date=date,
            type_=str(value.type_),
            winner_a=value.winners[0].name,
            winner_b=winner_b_str,
            winner_score=value.winner_score,
            loser_a=value.losers[0].name,
            loser_b=loser_b_str,
            loser_score=value.loser_score,
            duration=value.duration,
            session_index=session_idx,
        )
