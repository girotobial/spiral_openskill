import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main():
    data = pd.read_csv("./data/matches.csv")
    data["duration"] = pd.to_timedelta(
        data["duration"],
    )
    data["warmup"] = data["session_index"].apply(
        lambda i: "warmup" if i < 4 else "normal"
    )
    data["margin"] = data["winner_score"] - data["loser_score"]
    data["total_points"] = data["winner_score"] + data["loser_score"]

    data["duration_minutes"] = data["duration"].apply(lambda t: t.total_seconds() / 60)

    normal = data[data["session_index"] >= 4]
    print(normal["duration_minutes"].describe())

    alpha = 1 / 16
    print(
        f"{1 - alpha: .0%} games finish in {normal['duration_minutes'].quantile(1 - alpha)} minutes."
    )

    sns.histplot(normal, x="duration_minutes", binwidth=1)
    plt.grid()
    plt.savefig("histogram.png")
    plt.clf()

    sns.regplot(data, x="total_points", y="duration_minutes")
    plt.grid()
    plt.savefig("scatter.png")
    plt.clf()

    sns.boxplot(data, x="duration_minutes", y="type_")
    plt.grid()
    plt.savefig("box.png")
    plt.clf()

    sns.swarmplot(data, x="duration_minutes", y="warmup")
    plt.tight_layout()
    plt.grid()
    plt.savefig("warmup.png")
    plt.clf()


if __name__ == "__main__":
    main()
