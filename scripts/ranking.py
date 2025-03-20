from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from openskill.models import PlackettLuce, PlackettLuceRating


class Player:
    def __init__(
        self,
        rating: PlackettLuceRating,
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


class Model:
    def __init__(self, name: str | None = None):
        self.players: dict[str, Player] = {}
        self.model = PlackettLuce()
        self.name = name if name is not None else ""

    def get_rating(self, name: str) -> PlackettLuceRating:
        if name not in self.players:
            player = Player(self.model.rating(name=name))
            self.players[name] = player
        return self.players[name].rating

    def set_rating(self, name: str, rating: PlackettLuceRating):
        player = self.players[name]
        player.rating = rating

    def get_player(self, name: str) -> Player:
        if name not in self.players:
            player = Player(self.model.rating(name=name))
            self.players[name] = player
        return self.players[name]

    def set_player(self, player: Player):
        self.players[player.name] = player

    def update_rankings(self, data: pd.DataFrame):
        for _, row in data.iterrows():
            winners = [
                self.get_player(row["winner_a"]),
                self.get_player(row["winner_b"]),
            ]
            losers = [self.get_player(row["loser_a"]), self.get_player(row["loser_b"])]

            # Update win and loss tracking for each player
            winners[0].won_with(winners[1].name)
            winners[1].won_with(winners[0].name)

            losers[0].lost_with(losers[1].name)
            losers[1].lost_with(losers[0].name)

            for winner in winners:
                for loser in losers:
                    winner.lost_against(loser.name)

            # Get scores
            winner_score = float(row["winner_score"])
            loser_score = float(row["loser_score"])
            scores = [winner_score, loser_score]

            margin = scores[0] - scores[1]

            for winner in winners:
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

            max_winner_mu = max(winner.rating.mu for winner in winners)
            min_winner_mu = min(winner.rating.mu for winner in winners)

            skill_gap_winners = max_winner_mu - min_winner_mu

            # Reduce rating boost for weaker players if skill gap is large
            penalty_factor = 1 / (1 + skill_gap_winners * 0.1)

            # Update Ratings
            [new_winners, new_losers] = self.model.rate(
                teams=[
                    [winner.rating for winner in winners],
                    [loser.rating for loser in losers],
                ],
                scores=scores,
            )

            # Apply penalty by blending new & old ratings for weaker winners
            for i, winner in enumerate(winners):
                if winner.rating.mu < max_winner_mu:
                    self.set_rating(
                        winner.name,
                        PlackettLuceRating(
                            mu=winner.rating.mu
                            + penalty_factor * (new_winners[i].mu - winner.rating.mu),
                            sigma=winner.rating.sigma,
                            name=winner.rating.name,
                        ),
                    )
                else:
                    self.set_rating(winner.name, new_winners[i])

            for new_loser in new_losers:
                self.set_rating(new_loser.name, new_loser)

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


@dataclass
class Team:
    player_one: Player
    player_two: Player

    def __eq__(self, other) -> bool:
        if self.player_one == other.player_one and self.player_two == other.player_two:
            return True
        if self.player_one == other.player_two and self.player_two == other.player_one:
            return True
        return False


def main():
    data_path = Path(__file__).parent.parent / "data"
    data = pd.read_csv(data_path / "matches.csv")
    data["score_diff"] = data["winner_score"] - data["loser_score"]
    data = data.sort_values(by="date", ascending=True)
    mixed = data[data["type_"] == "Mixed"]
    ladies = data[data["type_"] == "Ladies"]
    mens = data[data["type_"] == "Mens"]
    overall = data[data["type_"] != "Imbalanced Mixed"]

    mixed_model = Model("mixed")
    mens_model = Model("mens")
    ladies_model = Model("ladies")
    overall_model = Model("overall")

    mixed_model.update_rankings(mixed)
    mens_model.update_rankings(mens)
    ladies_model.update_rankings(ladies)
    overall_model.update_rankings(overall)

    for model in (mixed_model, mens_model, ladies_model, overall_model):
        df = model.results()
        df.to_csv(data_path / f"{model.name}_ratings.csv", index=False)


if __name__ == "__main__":
    main()
