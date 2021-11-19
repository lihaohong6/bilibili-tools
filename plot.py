import matplotlib.pyplot as plt


def plot(frequencies: list[int]):
    """Unusable for now"""
    fig, ax = plt.subplots()

    for x, y in enumerate(frequencies):
        ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)

        ax.set(xlim=(0, len(frequencies)),
               ylim=(0, max(frequencies)))

        plt.show()
