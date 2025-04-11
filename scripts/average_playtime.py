import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main():
    data = pd.read_csv("./data/matches.csv")
    data["duration"] = pd.to_timedelta(
        data["duration"],
    )
    data["duration_minutes"] = data["duration"].apply(lambda t: t.total_seconds() / 60)
    print(data["duration_minutes"].describe())

    alpha = 1 / 16
    print(
        f"{1-alpha: .0%} games finish in {data['duration_minutes'].quantile(1-alpha)} minutes."
    )

    sns.histplot(data, x="duration_minutes", binwidth=1)
    plt.show()

    data["margin"] = data["winner_score"] - data["loser_score"]

    sns.scatterplot(data, x="margin", y="duration_minutes", hue="type_")
    plt.show()

    sns.boxplot(data, x="duration_minutes", y="type_")
    plt.show()


if __name__ == "__main__":
    main()
