from typing import Sequence

from database import Database, Player
from openskill.models import ThurstoneMostellerFull, ThurstoneMostellerFullRating


def get_rankings(
    players: Sequence[Player], model: ThurstoneMostellerFull, db: Database
) -> list[ThurstoneMostellerFullRating]:
    rankings = []
    for player in players:
        latest_rank = db.rank_history.get_latest(player.id)
        if latest_rank:
            rankings.append(
                model.rating(mu=latest_rank.mu, sigma=latest_rank.sigma, name=player.id)
            )
        else:
            rankings.append(model.rating(name=player.id))
    return rankings


def main():
    db = Database(path="data.db", echo=False)
    with db:
        for club in db.clubs.all():
            model = ThurstoneMostellerFull()
            print(f"Club: {club.name}")
            for session in db.sessions.get_ordered(club.id):
                for match in db.matches.get_ordered(session.id):
                    winner_rankings = []
                    loser_rankings = []
                    winner_score = match.winner_score
                    loser_score = match.loser_score
                    for result in match.teams:
                        if result.winner:
                            winner_rankings.extend(
                                get_rankings(result.team.members, model, db)
                            )
                        else:
                            loser_rankings.extend(
                                get_rankings(result.team.members, model, db)
                            )
                    [new_winner_rankings, new_loser_rankings] = model.rate(
                        teams=[winner_rankings, loser_rankings],
                        scores=[winner_score, loser_score],
                    )
                    for new_ranking in new_winner_rankings + new_loser_rankings:
                        db.rank_history.new(
                            player_id=new_ranking.name,
                            match_id=match.id,
                            mu=new_ranking.mu,
                            sigma=new_ranking.sigma,
                        )
        db.commit()


if __name__ == "__main__":
    main()
