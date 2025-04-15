import csv
import datetime
import enum
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Generic, Iterator, Self, TypeVar

from bs4 import BeautifulSoup
from bs4.element import Tag

T = TypeVar("T")


class SafeList(list, Generic[T]):
    def get(self, index: int) -> T | None:
        try:
            return self[index]
        except IndexError:
            return None


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


def _extract_name(text: str) -> str:
    print(text)
    return " ".join(s for s in text.strip().split(" ")).strip()


def _extract_match(row: Tag) -> Match:
    tds = row.find_all("td")
    type_ = Type.from_match_type(tds[0].text.strip())
    # Extract winners (names only, no rankings)
    winners = tds[1]
    assert isinstance(winners, Tag)
    winner_players = SafeList(
        Player.from_span(span)  # type: ignore
        for span in winners.find_all("span", class_="strong")
    )

    # Extract losers (names only, no rankings)
    losers = tds[3]
    assert isinstance(losers, Tag)
    loser_players = SafeList(
        Player.from_span(span)  # type: ignore
        for span in losers.find_all("span", recursive=False)
    )

    score_str: str = tds[2].text.strip()
    score = [int(s) for s in score_str.split("-")]

    duration_str = tds[6].text.strip()
    (hours, minutes, seconds) = duration_str.split(":")
    duration = datetime.timedelta(
        hours=int(hours), minutes=int(minutes), seconds=int(seconds)
    )

    return Match(
        type_=type_,
        winners=winner_players,
        losers=loser_players,
        winner_score=score[0],
        loser_score=score[1],
        duration=duration,
    )


def process_html_page(page: Path) -> Iterator[MatchRow]:
    with open(page, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    matches = soup.find_all("tr", class_="completed-match")

    date_str = page.stem.split(" ")[0]
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    for i, match_ in enumerate(reversed(matches)):
        assert isinstance(match_, Tag)
        m = _extract_match(match_)
        yield MatchRow.from_match(m, date, i)


def main():
    root = Path(__file__).parent.parent
    data = root / "data"
    pages_dir = root / "ebadders_pages"

    rows = []
    field_names = None
    for page in pages_dir.glob("*.html"):
        for row in process_html_page(page):
            if field_names is None:
                field_names = [field.name for field in fields(row)]
            rows.append(asdict(row))

    with open(data / "matches.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
