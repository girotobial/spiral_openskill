from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from openskill.models import PlackettLuce, PlackettLuceRating


class Model:
    def __init__(self, name: str | None = None):
        self.players: dict[str, PlackettLuceRating] = {}
        self.model = PlackettLuce()
        self.name = name if name is not None else ""

    def get_rating(self, player: str) -> PlackettLuceRating:
        if player not in self.players:
            self.players[player] = self.model.rating(name=player)
        return self.players[player]

    def set_rating(self, name: str, rating: PlackettLuceRating):
        self.players[name] = rating

    def update_rankings(self, data: pd.DataFrame):
        for _, row in data.iterrows():
            winners = [
                self.get_rating(row["winner_a"]),
                self.get_rating(row["winner_b"]),
            ]
            losers = [self.get_rating(row["loser_a"]), self.get_rating(row["loser_b"])]

            max_winner_mu = max(winner.mu for winner in winners)
            min_winner_mu = min(winner.mu for winner in winners)

            skill_gap_winners = max_winner_mu - min_winner_mu

            # Reduce rating boost for weaker players if skill gap is large
            penalty_factor = 1 / (1 + skill_gap_winners * 0.1)

            winner_score = float(row["winner_score"])
            loser_score = float(row["loser_score"])
            scores = [winner_score, loser_score]

            # Update Ratings
            [new_winners, new_losers] = self.model.rate(
                teams=[winners, losers], scores=scores
            )

            # Apply penalty by blending new & old ratings for weaker winners
            for i, winner in enumerate(winners):
                if winner.mu < max_winner_mu:
                    self.set_rating(
                        winner.name,
                        PlackettLuceRating(
                            mu=winner.mu
                            + penalty_factor * (new_winners[i].mu - winner.mu),
                            sigma=winner.sigma,
                            name=winner.name,
                        ),
                    )
                else:
                    self.set_rating(winner.name, new_winners[i])

            for loser in new_losers:
                self.set_rating(loser.name, loser)

        def results(self) -> pd.DataFrame:
            return pd.DataFrame(
                [
                    {
                        "Player": player,
                        "Mu": rating.mu,
                        "Sigma": rating.sigma,
                        "Ordinal": rating.ordinal(),
                    }
                    for player, rating in self.players.items()
                ]
            )


@dataclass
class Team:
    player_one: str
    player_two: str

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
