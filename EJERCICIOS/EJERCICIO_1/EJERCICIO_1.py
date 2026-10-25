import multiprocessing as mp
import random
import time

def estimate_pi(seed: int, samples: int = 1_000_000) -> float:
    """Monte Carlo: fraction of random points that fall inside the unit quarter circle."""
    rng = random.Random(seed)
    inside = sum(rng.random()**2 + rng.random()**2 <= 1.0 for _ in range(samples))
    return 4 * inside / samples

def plot_speedup(procs: list[int], speedups: list[float], filename: str = "ex1_speedup.png") -> None:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(7, 5))
    plt.plot(procs, procs, "--", color="gray", label="Speedup ideal (S = p)")
    plt.plot(procs, speedups, "o-", color="tab:blue", label="Speedup medido")
    for p, s in zip(procs, speedups):
        plt.annotate(f"{s:.2f}x", (p, s), textcoords="offset points", xytext=(6, -12))
    plt.xlabel("Número de procesos")
    plt.ylabel("Speedup (t_seq / t_par)")
    plt.title("Ejercicio 1: speedup de estimate_pi")
    plt.xticks(procs)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if input("¿Guardar la gráfica? (s/n): ").strip().lower() == "s":
        plt.savefig(filename, dpi=150)
        print(f"Gráfica guardada en {filename}")
    if input("¿Mostrar la gráfica? (s/n): ").strip().lower() == "s":
        plt.show()
    plt.close()

if __name__ == "__main__":
    seeds = list(range(8))  # 8 independent runs, one seed each
    procs = [1, 2, 4, 8]

    # 1. Sequential Looping
    t0 = time.perf_counter()
    seq_results = [estimate_pi(s) for s in seeds]
    t_seq = time.perf_counter() - t0
    print(f"Sequential wall-clock: {t_seq:.3f} s")

    # 2. Parallel Pool Execution con 1, 2, 4 y 8 procesos
    speedups = []
    for p in procs:
        t0 = time.perf_counter()
        with mp.Pool(processes=p) as pool:
            par_results = pool.map(estimate_pi, seeds)
        t_par = time.perf_counter() - t0
        speedups.append(t_seq / t_par)
        print(f"Parallel ({p} procs): {t_par:.3f} s (Speedup: {t_seq/t_par:.2f}x)")

    print(f"pi estimate (mean of {len(seeds)} runs): {sum(par_results) / len(par_results):.5f}")

    plot_speedup(procs, speedups)