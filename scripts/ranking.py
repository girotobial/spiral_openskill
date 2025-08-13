from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import pandas as pd
from openskill.models import ThurstoneMostellerFull, ThurstoneMostellerFullRating
from tqdm import tqdm
from common import Type

MIN_MU = 10
MAX_SIGMA = 8


class Player:
    def __init__(
        self,
        rating: ThurstoneMostellerFullRating,
        wins: int = 0,
        game: int = 0,
        avg_win_margin: float = 0,
        avg_loss_margin: float = 0,
    ):
        self.rating = rating
        self.wins = wins
        self.games = game
        self.avg_win_margin = avg_win_margin
        self.avg_loss_margin = avg_loss_margin
        self.wins_with: dict[str, int] = {}
        self.loses_with: dict[str, int] = {}
        self.loses_against: dict[str, int] = {}

    @property
    def name(self) -> str:
        return self.rating.name

    def win_rate(self) -> float:
        return self.wins / self.games

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __repr__(self) -> str:
        return f"Player(rating={self.rating}, wins={self.wins}, games={self.games})"

    def __str__(self) -> str:
        return f"{self.name}"

    def __hash__(self) -> int:
        return hash(self.name)

    def __lt__(self, other) -> bool:
        return self.name < other.name

    def won_with(self, name: str):
        player_total = self.wins_with.get(name)
        if player_total is None:
            player_total = 0
        player_total = player_total + 1
        self.wins_with[name] = player_total

    def lost_with(self, name: str):
        player_total = self.loses_with.get(name)
        if player_total is None:
            player_total = 0
        player_total = player_total + 1
        self.loses_with[name] = player_total

    def wins_with_most(self) -> str:
        best_player = ""
        best_total = 0
        for player, total in self.wins_with.items():
            if total > best_total:
                best_total = total
                best_player = player
        return best_player

    def lost_with_most(self) -> str:
        worst_player = ""
        biggest_loss = 0
        for player, total in self.loses_with.items():
            if total > biggest_loss:
                biggest_loss = total
                worst_player = player
        return worst_player

    def lost_against(self, name: str):
        player_total = self.loses_against.get(name)
        if player_total is None:
            player_total = 0
        player_total = player_total + 1
        self.loses_against[name] = player_total

    def lost_against_most(self) -> str:
        nemesis = ""
        total_games = 0
        for player, total in self.loses_against.items():
            if total > total_games:
                total_games = total
                nemesis = player
        return nemesis


class Team:
    player_one: Player
    player_two: Player

    def __init__(self, player_one: Player, player_two: Player):
        self.player_one = player_one
        self.player_two = player_two

    def __eq__(self, other) -> bool:
        if self.player_one == other.player_one and self.player_two == other.player_two:
            return True
        if self.player_one == other.player_two and self.player_two == other.player_one:
            return True
        return False

    def __str__(self) -> str:
        return f"[{self.player_one}, {self.player_two}]"

    def __repr__(self) -> str:
        return f"Team({self.player_one}, {self.player_two})"

    @property
    def players(self) -> tuple[Player, Player]:
        return (self.player_one, self.player_two)


@dataclass
class Match:
    team_one: Team
    team_two: Team

    def __str__(self) -> str:
        return f"{self.team_one} v {self.team_two}"

    def __hash__(self) -> int:
        players = tuple(sorted((*self.team_one.players, *self.team_two.players)))
        return hash(players)

    def players(self) -> list[str]:
        return [
            *[player.name for player in self.team_one.players],
            *[player.name for player in self.team_two.players],
        ]


class Model:
    def __init__(self, name: str | None = None):
        self.players: dict[str, Player] = {}
        self.model = ThurstoneMostellerFull()
        self.name = name if name is not None else ""

    def get_rating(self, name: str) -> ThurstoneMostellerFullRating:
        if name not in self.players:
            player = Player(self.model.rating(name=name))
            self.players[name] = player
        return self.players[name].rating

    def set_rating(self, name: str, rating: ThurstoneMostellerFullRating):
        player = self.players[name]
        player.rating = rating

    def get_player(self, name: str) -> Player:
        if name not in self.players:
            player = Player(self.model.rating(name=name))
            self.players[name] = player
        return self.players[name]

    def set_player(self, player: Player):
        self.players[player.name] = player

    def update_rankings(
        self, winners: list[Player], losers: list[Player], scores: tuple[float, float]
    ):
        winner_ratings = [winner.rating for winner in winners]
        losers_ratings = [loser.rating for loser in losers]

        # Update Ratings
        [new_winners, new_losers] = self.model.rate(
            teams=[winner_ratings, losers_ratings],
            scores=list(scores),
        )

        players = [*new_winners, *new_losers]

        for player in players:
            self.set_rating(player.name, player)

    def update_stats(
        self, winners: list[Player], losers: list[Player], scores: tuple[float, float]
    ):
        # Update win and loss tracking for each player
        winners[0].won_with(winners[1].name)
        winners[1].won_with(winners[0].name)

        losers[0].lost_with(losers[1].name)
        losers[1].lost_with(losers[0].name)

        margin = scores[0] - scores[1]
        for winner in winners:
            for loser in losers:
                loser.lost_against(winner.name)

            winner.games = winner.games + 1
            winner.wins = winner.wins + 1

            old_wins = winner.wins - 1 if winner.wins > 0 else winner.wins
            old_average = winner.avg_win_margin * old_wins

            winner.avg_win_margin = (old_average + margin) / winner.wins
            self.set_player(winner)

        for loser in losers:
            loser.games = loser.games + 1
            losses = loser.games - loser.wins
            old_losses = losses - 1 if losses > 0 else losses
            old_average_loss = loser.avg_loss_margin * old_losses

            loser.avg_loss_margin = (old_average_loss + margin) / losses
            self.set_player(loser)

    def update(self, data: pd.DataFrame):
        for _, row in tqdm(data.iterrows(), desc=f"{self.name} ranking update"):
            winners = [
                self.get_player(row["winner_a"]),
                self.get_player(row["winner_b"]),
            ]
            losers = [self.get_player(row["loser_a"]), self.get_player(row["loser_b"])]

            # Get scores
            winner_score = float(row["winner_score"])
            loser_score = float(row["loser_score"])
            scores = (winner_score, loser_score)

            self.update_stats(winners, losers, scores)
            self.update_rankings(winners, losers, scores)

    def results(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "Player": name,
                    "Mu": player.rating.mu,
                    "Sigma": player.rating.sigma,
                    "Ordinal": player.rating.ordinal(),
                    "Wins": player.wins,
                    "Total Games": player.games,
                    "Win/Loss": player.win_rate(),
                    "Average Win Margin": player.avg_win_margin,
                    "Average Loss Margin": player.avg_loss_margin,
                    "Player won with most": player.wins_with_most(),
                    "Player lost with most": player.lost_with_most(),
                    "Players beaten by most": player.lost_against_most(),
                }
                for name, player in self.players.items()
            ]
        ).sort_values(by=["Ordinal"], ascending=False)

    def predict_draw(self, match: Match) -> float:
        teams = [
            [player.rating for player in match.team_one.players],
            [player.rating for player in match.team_two.players],
        ]
        return self.model.predict_draw(teams=teams)

    def predict_draws(self) -> dict[Match, float]:
        players = self.players.items()

        unique_matches = set()
        unique_groups = set()

        for group in tqdm(
            combinations(players, 4), desc=f"{self.name} draw predictions"
        ):
            group = tuple(sorted(group))
            if group in unique_groups:
                continue
            unique_groups.add(group)
            for team1 in combinations(group, 2):
                team2 = tuple(sorted(set(group) - set(team1)))
                match_ = Match(
                    Team(team1[0][1], team1[1][1]), Team(team2[0][1], team2[1][1])
                )
                unique_matches.add(match_)

        results: dict[Match, float] = {}

        for match in unique_matches:
            results[match] = self.predict_draw(match)

        return results

    def predict_draws_df(self) -> pd.DataFrame:
        draws = self.predict_draws()
        return pd.DataFrame(
            [
                {
                    "Player 1": match.team_one.players[0],
                    "Player 2:": match.team_one.players[1],
                    "Player 3:": match.team_two.players[0],
                    "Player 4:": match.team_two.players[1],
                    "Draw Probability": score,
                }
                for match, score in tqdm(draws.items())
            ]
        ).sort_values(by="Draw Probability", ascending=False)


def produce_ranks(data: pd.DataFrame) -> pd.DataFrame:
    model = Model()
    model.update(data)
    return model.results()


def main():
    data_path = Path(__file__).parent.parent / "data"
    data = pd.read_csv(data_path / "matches.csv")
    data["score_diff"] = data["winner_score"] - data["loser_score"]
    data = data.sort_values(by="date", ascending=True)

    clubs = data["club"].unique()

    for club in clubs:
        club_data = data[data["club"] == club]
        for type_ in Type:
            if type_ == Type.UNDEFINED:
                continue
            filtered_data = club_data[club_data["type_"] == str(type_).upper()]
            if filtered_data.shape[0] == 0:
                continue
            results = produce_ranks(filtered_data)
            results.to_csv(data_path / f"{club}_{type_}.csv", index=False)
        produce_ranks(club_data).to_csv(data_path / f"{club}_overall.csv", index=False)

    for type_ in Type:
        if type_ == Type.UNDEFINED:
            continue
        filtered_data = data[data["type_"] == str(type_).upper()]
        if filtered_data.shape[0] == 0:
            continue
        model = Model(f"all_{type_}")
        model.update(filtered_data)
        results = model.results()
        results.to_csv(data_path / f"all_{type_}.csv", index=False)

    produce_ranks(data).to_csv(data_path / f"all_overall.csv", index=False)


if __name__ == "__main__":
    main()
