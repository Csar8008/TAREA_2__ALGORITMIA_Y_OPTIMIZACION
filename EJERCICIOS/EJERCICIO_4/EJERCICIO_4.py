import math
import random
import statistics
import time

def tour_length(points, tour) -> float:
    return sum(math.dist(points[tour[i]], points[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))

def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    """Reverse route[i..k]: removes edges (i-1, i) and (k, k+1)."""
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]

def simulated_annealing(points, tour, schedule, iterations):
    """SA for TSP: random 2-opt neighbour, accept worse tours with probability e^(-delta / T)."""
    n, current = len(tour), tour_length(points, tour)
    best, history = current, []
    for t in range(iterations):
        T = schedule(t)
        i, k = sorted(random.sample(range(1, n), 2))      # Diff 1: random pick (not best)
        a, b = points[tour[i - 1]], points[tour[i]]
        c, d = points[tour[k]], points[tour[(k + 1) % n]]
        delta = math.dist(a, c) + math.dist(b, d) - math.dist(a, b) - math.dist(c, d)
        if delta < 0 or random.random() < math.exp(-delta / T):   # Diff 2: accept bad moves
            tour, current = two_opt_move(tour, i, k), current + delta
        best = min(best, current)
        if t % 100 == 0:
            history.append(current)
    return tour, best, history

def make_schedules(iterations: int, T0: float = 10.0, Tf: float = 0.01) -> dict:
    return {"Lineal": lambda t: T0 - (T0 - Tf) * t / iterations,
            "Exponencial": lambda t: T0 * (Tf / T0) ** (t / iterations),
            "Logarítmico": lambda t: T0 * math.log(2) / math.log(2 + t)}

def guardar_o_mostrar(filename: str) -> None:
    import matplotlib.pyplot as plt
    if input("¿Guardar la gráfica? (s/n): ").strip().lower() == "s":
        plt.savefig(filename, dpi=150)
        print(f"Gráfica guardada en {filename}")
    if input("¿Mostrar la gráfica? (s/n): ").strip().lower() == "s":
        plt.show()
    plt.close()

def plot_convergencia(schedules, mean_hist, iterations, filename: str = "ex4_convergencia.png") -> None:
    import matplotlib.pyplot as plt
    ts = list(range(0, iterations, 100))
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.5))
    for name, schedule in schedules.items():
        ax1.plot(ts, [schedule(t) for t in ts], label=name)
        ax2.plot(ts, mean_hist[name], label=name)
        ax3.plot([schedule(t) for t in ts], mean_hist[name], label=name)
    ax1.set_yscale("log")
    ax1.set_xlabel("Iteración"); ax1.set_ylabel("Temperatura T"); ax1.set_title("Esquemas de enfriamiento")
    ax2.set_xlabel("Iteración"); ax2.set_ylabel("Costo (longitud del tour)"); ax2.set_title("Costo vs. iteraciones")
    ax3.set_xscale("log"); ax3.invert_xaxis()
    ax3.set_xlabel("Temperatura T (enfriando →)"); ax3.set_ylabel("Costo (longitud del tour)"); ax3.set_title("Costo vs. temperatura")
    for ax in (ax1, ax2, ax3):
        ax.grid(alpha=0.3); ax.legend()
    fig.suptitle("Ejercicio 4: convergencia del recocido simulado (promedio de las corridas)")
    fig.tight_layout()
    guardar_o_mostrar(filename)

def plot_comparacion(resultados: dict, budgets: list[int], filename: str = "ex4_comparacion.png") -> None:
    import matplotlib.pyplot as plt
    nombres, colores, ancho = list(resultados), ["tab:blue", "tab:orange", "tab:green"], 0.26
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for j, name in enumerate(nombres):
        medias = [statistics.mean(resultados[name][b][0]) for b in budgets]
        desv = [statistics.stdev(resultados[name][b][0]) for b in budgets]
        xs = [i + (j - 1) * ancho for i in range(len(budgets))]
        barras = ax.bar(xs, medias, ancho, yerr=desv, capsize=3, color=colores[j], label=name)
        ax.bar_label(barras, labels=[f"{m:.1f}" for m in medias], padding=2, fontsize=8)
    t_medio = [statistics.mean(statistics.mean(resultados[nm][b][1]) for nm in nombres) for b in budgets]
    ax.set_xticks(range(len(budgets)))
    ax.set_xticklabels([f"{b:,} iter.\n≈ {t:.2f} s" for b, t in zip(budgets, t_medio)])
    ax.set_xlabel("Presupuesto de cómputo (iteraciones y tiempo de ejecución promedio)")
    ax.set_ylabel("Longitud del mejor tour (menor es mejor)")
    ax.set_title("Ejercicio 4: tiempo de ejecución vs. calidad por esquema de enfriamiento (media ± desv. est.)")
    ax.legend()
    fig.tight_layout()
    guardar_o_mostrar(filename)

if __name__ == "__main__":
    random.seed(7)
    n, runs, budgets = 30, 20, [5_000, 15_000, 30_000, 100_000]
    points = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(n)]

    resultados = {name: {} for name in make_schedules(1)}
    historias = {name: [] for name in resultados}
    for budget in budgets:
        for name, schedule in make_schedules(budget).items():
            costos, tiempos = [], []
            for _ in range(runs):
                start = random.sample(range(n), n)
                t0 = time.perf_counter()
                tour, best, history = simulated_annealing(points, start, schedule, budget)
                tiempos.append(time.perf_counter() - t0)
                costos.append(best)
                if budget == 30_000:
                    historias[name].append(history)
            resultados[name][budget] = (costos, tiempos)

    print(f"{n} ciudades, {runs} corridas por esquema y presupuesto (T0 = 10, Tf = 0.01)")
    print(f"{'Iteraciones':>12s}  " + "  ".join(f"{name:>22s}" for name in resultados))
    for budget in budgets:
        print(f"{budget:>12,}  " + "  ".join(
            f"{statistics.mean(resultados[nm][budget][0]):>8.2f} ({statistics.mean(resultados[nm][budget][1]):>5.2f} s)   "
            for nm in resultados))

    mean_hist = {name: [statistics.mean(h[j] for h in historias[name]) for j in range(len(historias[name][0]))]
                 for name in resultados}
    plot_convergencia(make_schedules(30_000), mean_hist, 30_000)
    plot_comparacion(resultados, budgets)