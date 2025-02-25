from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import pandas as pd
from openskill.models import PlackettLuce, PlackettLuceRating


class PageRankModel:
    def __init__(self):
        self.graph = nx.DiGraph()

    def update_rankings(self, data: pd.DataFrame):
        for _, row in data.iterrows():
            margin = row["margin"]
            winner_a = row["winner_a"]
            winner_b = row["winner_b"]
            loser_a = row["loser_a"]
            loser_b = row["loser_b"]
            for winner in (winner_a, winner_b):
                for loser in (loser_a, loser_b):
                    self.graph.add_edge(loser, winner, weight=margin)

    def get_rankings(self) -> pd.DataFrame:
        scores = nx.pagerank(self.graph, weight="weight")

        rankings = pd.DataFrame(list(scores.items()), columns=["Player", "PageRank"])
        rankings = rankings.sort_values(by="PageRank", ascending=False)
        return rankings


class PLModel:
    def __init__(self):
        self.players: dict[str, PlackettLuceRating] = {}
        self.model = PlackettLuce()

    def get_rating(self, player: str) -> PlackettLuceRating:
        if player not in self.players:
            self.players[player] = self.model.rating(name=player)
        return self.players[player]

    def set_rating(self, name: str, rating: PlackettLuceRating):
        self.players[name] = rating

    def update_rankings(self, data: pd.DataFrame):
        for _, row in data.iterrows():
            for player in [
                row["winner_a"],
                row["winner_b"],
                row["loser_a"],
                row["loser_b"],
            ]:
                self.get_rating(player)
            # Update ratings after each match
        for _, row in data.iterrows():
            winners = [
                self.get_rating(row["winner_a"]),
                self.get_rating(row["winner_b"]),
            ]
            losers = [
                self.get_rating(row["loser_a"]),
                self.get_rating(row["loser_b"]),
            ]
            winner_score = float(row["winner_score"])
            loser_score = float(row["loser_score"])
            scores = [winner_score, loser_score]

            # Update Ratings
            [new_winners, new_losers] = self.model.rate(
                teams=[winners, losers], scores=scores
            )

            # Store new ratings
            self.set_rating(row["winner_a"], new_winners[0])
            self.set_rating(row["winner_b"], new_winners[1])
            self.set_rating(row["loser_a"], new_losers[0])
            self.set_rating(row["loser_b"], new_losers[1])

    def get_rankings(self) -> pd.DataFrame:
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
    data["margin"] = data["winner_score"] - data["loser_score"]
    mixed = data[data["type_"] == "Mixed"]
    ladies = data[data["type_"] == "Ladies"]
    mens = data[data["type_"] == "Mens"]
    overall = data[data["type_"] != "Imbalanced Mixed"]

    mixed_model = PLModel()
    mens_model = PLModel()
    ladies_model = PLModel()
    overall_model = PLModel()
    overall_pg = PageRankModel()

    mixed_model.update_rankings(mixed)
    overall_pg.update_rankings(overall)
    mens_model.update_rankings(mens)
    ladies_model.update_rankings(ladies)
    overall_model.update_rankings(overall)

    mixed_ratings_df = mixed_model.get_rankings()
    overall_pg_df = overall_pg.get_rankings()

    mens_ratings_df = mens_model.get_rankings()
    ladies_ratings_df = ladies_model.get_rankings()
    overall_ratings_df = overall_model.get_rankings()

    ladies_ratings_df.to_csv(data_path / "ladies_ratings.csv", index=False)
    mens_ratings_df.to_csv(data_path / "mens_ratings.csv", index=False)
    overall_pg_df.to_csv(data_path / "overall_pg.csv", index=False)
    mixed_ratings_df.to_csv(data_path / "mixed_ratings.csv", index=False)
    overall_ratings_df.to_csv(data_path / "overall_ratings.csv", index=False)


if __name__ == "__main__":
    main()
