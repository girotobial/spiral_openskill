import csv
import datetime
from dataclasses import asdict, fields
from pathlib import Path
from typing import Iterator

from bs4 import BeautifulSoup
from bs4.element import Tag
from common import Match, MatchRow, Player, SafeList, Type
from database import Club, Database
from database import Match as DbMatch
from database import Result, Session


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


def add_page_to_db(database: Database, page: Path, club: Club) -> None:
    game_session: Session | None = None
    for row in process_html_page(page):
        if row.session_index == 0:
            if database.sessions.get(date=row.date, club_id=club.id) is None:
                print(f"Session with date={row.date} and {club.id} not found")
                game_session = Session(date=row.date)
                club.sessions.append(game_session)
            else:
                return None

        match = DbMatch(
            session_index=row.session_index,
            winner_score=row.winner_score,
            loser_score=row.loser_score,
            margin=row.winner_score - row.loser_score,
            duration=int(row.duration.total_seconds()),
        )
        game_session.matches.append(match)

        winning_players = [
            database.players.get_or_create(name)
            for name in (row.winner_a, row.winner_b)
        ]
        winning_team = database.teams.get_or_create(winning_players)

        win_result = Result(team=winning_team, winner=True, match=match)
        database.session.add(win_result)

        losing_players = [
            database.players.get_or_create(name) for name in (row.loser_a, row.loser_b)
        ]
        losing_team = database.teams.get_or_create(losing_players)
        lose_result = Result(team=losing_team, winner=False, match=match)
        database.session.add(lose_result)

    database.commit()


def main():
    root = Path(__file__).parent.parent
    data = root / "data"
    pages_root = root / "ebadders_pages"
    clubs = ["spiral", "drop_shotters"]

    database = Database("./data.db")

    rows = []
    field_names = None
    with database:
        for club_name in clubs:
            pages_dir = pages_root / club_name
            club = database.clubs.get_or_create(club_name)
            for page in pages_dir.glob("*.html"):
                add_page_to_db(database, page, club)

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
