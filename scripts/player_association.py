from csv import DictReader
from pathlib import Path

from database import Database


def main():
    database = Database("./data.db", echo=True)
    data_path = Path(__file__).parent.parent / "data" / "player_person_map.csv"

    with open(data_path) as csvfile:
        reader = DictReader(csvfile)
        with database:
            for row in reader:
                player_name = row["player_name"]
                person_name = row["person"]
                player = database.players.get(player_name)
                person = database.people.get_or_create(person_name)
                player.person = person
            database.commit()


if __name__ == "__main__":
    main()
