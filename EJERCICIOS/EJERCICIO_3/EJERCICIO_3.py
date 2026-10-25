import math
import random
import statistics

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

def nearest_neighbor(points, start: int) -> list[int]:
    tour, left = [start], set(range(len(points))) - {start}
    while left:
        tour.append(min(left, key=lambda c: math.dist(points[tour[-1]], points[c])))
        left.remove(tour[-1])
    return tour

def plot_comparacion(mejoras: dict, costos: dict, filename: str = "ex3_2opt.png") -> None:
    import matplotlib.pyplot as plt
    nombres, colores = list(mejoras), ["tab:red", "tab:green"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    for ax, datos, ylabel, titulo in [(ax1, mejoras, "Número de mejoras 2-opt", "Mejoras hasta el óptimo local"),
                                      (ax2, costos, "Longitud del tour final", "Calidad del óptimo local alcanzado")]:
        medias = [statistics.mean(datos[nm]) for nm in nombres]
        desv = [statistics.stdev(datos[nm]) for nm in nombres]
        barras = ax.bar(nombres, medias, yerr=desv, capsize=8, color=colores)
        for b, m, d in zip(barras, medias, desv):
            ax.text(b.get_x() + b.get_width() / 2, m + d, f"{m:.1f}", ha="center", va="bottom", fontsize=11)
        ax.set_ylim(0, max(m + d for m, d in zip(medias, desv)) * 1.12)
        ax.set_ylabel(ylabel)
        ax.set_title(titulo)
    fig.suptitle("Ejercicio 3: 2-opt desde inicio aleatorio vs. Vecino Más Cercano (media ± desv. est.)")
    fig.tight_layout()

    if input("¿Guardar la gráfica? (s/n): ").strip().lower() == "s":
        plt.savefig(filename, dpi=150)
        print(f"Gráfica guardada en {filename}")
    if input("¿Mostrar la gráfica? (s/n): ").strip().lower() == "s":
        plt.show()
    plt.close()

if __name__ == "__main__":
    random.seed(42)
    n, instances = 30, 100
    mejoras = {"Aleatorio": [], "Vecino Más Cercano": []}
    costos = {"Aleatorio": [], "Vecino Más Cercano": []}
    inicial = {"Aleatorio": [], "Vecino Más Cercano": []}

    for _ in range(instances):
        points = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(n)]
        starts = {"Aleatorio": random.sample(range(n), n),
                  "Vecino Más Cercano": nearest_neighbor(points, random.randrange(n))}
        for name, start in starts.items():
            tour, length, k = two_opt(points, start)
            mejoras[name].append(k)
            costos[name].append(length)
            inicial[name].append(tour_length(points, start))

    print(f"{instances} instancias de {n} ciudades")
    for name in mejoras:
        print(f"{name:18s} L inicial = {statistics.mean(inicial[name]):7.2f}  "
              f"mejoras = {statistics.mean(mejoras[name]):5.1f}"
              f"L final = {statistics.mean(costos[name]):.2f}")
    a, b = mejoras.values()
    ca, cb = costos.values()
    print(f"Nearest neighbor necesitó menos mejoras en {sum(y < x for x, y in zip(a, b))}/{instances} instancias")
    print(f"Nearest neighbor terminó con mejor tour en {sum(y < x for x, y in zip(ca, cb))}/{instances} instancias")

    plot_comparacion(mejoras, costos)