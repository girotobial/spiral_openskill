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

    @property
    def name(self) -> str:
        return self.rating.name

    def win_rate(self) -> float:
        return self.wins / self.games

    def __eq__(self, other) -> bool:
        return self.name == other.name


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
                }
                for name, player in self.players.items()
            ]
        )


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
