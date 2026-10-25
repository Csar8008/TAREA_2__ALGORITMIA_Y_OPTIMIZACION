import itertools
import math
import random
import statistics

def mst_prim(points: list[tuple[float, float]]) -> dict[int, list[int]]:
    """Prim's algorithm from city 0; returns the tree as {node: children}."""
    best = {v: (math.dist(points[0], points[v]), 0) for v in range(1, len(points))}
    children = {v: [] for v in range(len(points))}
    while best:
        v = min(best, key=lambda u: best[u][0])
        children[best.pop(v)[1]].append(v)          # add the cheapest edge to the tree
        for u in best:
            d = math.dist(points[v], points[u])
            if d < best[u][0]:
                best[u] = (d, v)
    return children

def preorder(children: dict[int, list[int]], root: int = 0) -> list[int]:
    """Walk around the tree; visiting each city once = shortcutting repeated cities."""
    return [root] + [c for child in children[root] for c in preorder(children, child)]

def tour_length(points, tour) -> float:
    return sum(math.dist(points[tour[i]], points[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))

def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    """Reverse route[i..k]: removes edges (i-1, i) and (k, k+1)."""
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

def two_opt(points, tour):
    """Local search: apply the first improving 2-opt move until none is left."""
    best, improvements, improved = tour_length(points, tour), 0, True
    while improved:
        improved = False
        for i in range(1, len(tour) - 1):
            for k in range(i + 1, len(tour)):
                new = two_opt_move(tour, i, k)
                if tour_length(points, new) < best:
                    tour, best, improvements, improved = new, tour_length(points, new), improvements + 1, True
                    break
            if improved:
                break
    return tour, best, improvements

def simulated_annealing(points, tour, schedule, iterations):
    """SA for TSP: random 2-opt neighbour, accept worse tours with probability e^(-delta / T)."""
    n, current = len(tour), tour_length(points, tour)
    best = current
    for t in range(iterations):
        T = schedule(t)
        i, k = sorted(random.sample(range(1, n), 2))
        a, b = points[tour[i - 1]], points[tour[i]]
        c, d = points[tour[k]], points[tour[(k + 1) % n]]
        delta = math.dist(a, c) + math.dist(b, d) - math.dist(a, b) - math.dist(c, d)
        if delta < 0 or random.random() < math.exp(-delta / T):
            tour, current = two_opt_move(tour, i, k), current + delta
        best = min(best, current)
    return tour, best

def guardar_o_mostrar(filename: str) -> None:
    import matplotlib.pyplot as plt
    if input("¿Guardar la gráfica? (s/n): ").strip().lower() == "s":
        plt.savefig(filename, dpi=150)
        print(f"Gráfica guardada en {filename}")
    if input("¿Mostrar la gráfica? (s/n): ").strip().lower() == "s":
        plt.show()
    plt.close()

def plot_razon(ratios: dict, filename: str = "ex5_razon.png") -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = [1 + 0.05 * j for j in range(22)]
    for name, color in [("MST", "tab:blue"), ("MST + 2-opt", "tab:green")]:
        ax.hist(ratios[name], bins=bins, alpha=0.6, color=color, edgecolor="white",
                label=f"{name} (media {statistics.mean(ratios[name]):.3f})")
    ax.axvline(2, color="red", linestyle="--", linewidth=2, label="Límite teórico = 2")
    ax.set_xlim(1, 2.1)
    ax.set_xlabel("Razón de aproximación  C obtenido / C óptimo")
    ax.set_ylabel("Número de instancias")
    ax.set_title("Ejercicio 5: razón de aproximación en 100 instancias de 9 ciudades")
    ax.legend()
    fig.tight_layout()
    guardar_o_mostrar(filename)

def plot_comparacion(costos: dict, optimos: list, filename: str = "ex5_comparacion.png") -> None:
    import matplotlib.pyplot as plt
    nombres = list(costos)
    colores = ["tab:blue", "tab:green", "tab:orange", "tab:red"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    medias = [statistics.mean(costos[nm]) for nm in nombres]
    desv = [statistics.stdev(costos[nm]) for nm in nombres]
    barras = ax1.bar(nombres, medias, yerr=desv, capsize=6, color=colores)
    for b, m, d in zip(barras, medias, desv):
        ax1.text(b.get_x() + b.get_width() / 2, m + d, f"{m:.2f}", ha="center", va="bottom", fontsize=10)
    ax1.axhline(statistics.mean(optimos), color="black", linestyle="--",
                label=f"Óptimo (media {statistics.mean(optimos):.2f})")
    ax1.set_ylim(0, max(m + d for m, d in zip(medias, desv)) * 1.12)
    ax1.set_ylabel("Longitud del tour")
    ax1.set_title("Costo obtenido (media ± desv. est.)")
    ax1.legend()
    ax1.tick_params(axis="x", labelsize=9)

    razones = [statistics.mean(c / o for c, o in zip(costos[nm], optimos)) for nm in nombres]
    barras = ax2.bar(nombres, razones, color=colores)
    for b, r in zip(barras, razones):
        ax2.text(b.get_x() + b.get_width() / 2, r, f"{r:.3f}", ha="center", va="bottom", fontsize=10)
    ax2.axhline(1, color="black", linestyle="--", label="Óptimo = 1")
    ax2.set_ylim(0.9, max(razones) * 1.05)
    ax2.set_ylabel("Razón promedio  C obtenido / C óptimo")
    ax2.set_title("Razón de aproximación promedio")
    ax2.legend()
    ax2.tick_params(axis="x", labelsize=9)

    fig.suptitle("Ejercicio 5: MST puro, MST + 2-opt, búsqueda local y recocido simulado")
    fig.tight_layout()
    guardar_o_mostrar(filename)

if __name__ == "__main__":
    random.seed(7)
    n, instances, iterations = 9, 100, 5_000
    T0, Tf = 10.0, 0.01
    schedule = lambda t: T0 * (Tf / T0) ** (t / iterations)    # enfriamiento exponencial

    costos = {"MST": [], "MST + 2-opt": [], "Búsqueda local": [], "Recocido simulado": []}
    optimos = []

    for _ in range(instances):
        points = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(n)]
        optimos.append(min(tour_length(points, (0,) + p) for p in itertools.permutations(range(1, n))))  # brute force: 8! tours

        mst_tour = preorder(mst_prim(points))
        costos["MST"].append(tour_length(points, mst_tour))
        costos["MST + 2-opt"].append(two_opt(points, mst_tour)[1])
        costos["Búsqueda local"].append(two_opt(points, random.sample(range(n), n))[1])
        costos["Recocido simulado"].append(simulated_annealing(points, random.sample(range(n), n), schedule, iterations)[1])

    ratios = {name: [c / o for c, o in zip(cs, optimos)] for name, cs in costos.items()}

    print(f"{instances} instancias de {n} ciudades (óptimo por fuerza bruta)")
    print(f"{'Método':18s} {'Costo medio':>11s} {'Razón media':>12s} {'Razón máx':>10s} {'% óptimo':>9s}")
    print(f"{'Óptimo':18s} {statistics.mean(optimos):>11.2f} {1:>12.3f} {1:>10.3f} {100:>8.0f}%")
    for name in costos:
        r = ratios[name]
        print(f"{name:18s} {statistics.mean(costos[name]):>11.2f} {statistics.mean(r):>12.3f} {max(r):>10.3f} "
              f"{100 * sum(x < 1 + 1e-9 for x in r) / instances:>8.0f}%")

    plot_razon(ratios)
    plot_comparacion(costos, optimos)