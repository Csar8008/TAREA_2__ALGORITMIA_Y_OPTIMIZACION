def obtener_peso(objeto):
    return objeto[2]

def obtener_ratio(objeto):
    return -objeto[1] / objeto[2]

def greedy(objetos, cap, criterio):
    total_v, total_w, llevar = 0, 0, []
    for name, v, w in sorted(objetos, key=criterio):
        if total_w + w <= cap:
            llevar.append(name); total_v += v; total_w += w
    return total_v, total_w, llevar

def mostrar_tabla_objetos(objetos, cap):
    print("=" * 40)
    print("INSTANCIA DEL PROBLEMA DE LA MOCHILA")
    print("=" * 40)
    print(f"Capacidad de la mochila: {cap}\n")
    print(f"{'Objeto':8s} {'Valor':>8s} {'Peso':>8s} {'Valor/Peso':>12s}")
    print("-" * 40)
    for name, v, w in objetos:
        print(f"{name:8s} {v:>8d} {w:>8d} {v / w:>12.2f}")
    print("-" * 40)
    print(f"{'Total':8s} {sum(o[1] for o in objetos):>8d} {sum(o[2] for o in objetos):>8d}")
    print()

def plot_comparacion(resultados: dict, cap: int, filename: str = "ex2_knapsack.png") -> None:
    import matplotlib.pyplot as plt
    etiquetas = [f"{m}\n{{{', '.join(r[2])}}}" for m, r in resultados.items()]
    valores = [r[0] for r in resultados.values()]
    pesos = [r[1] for r in resultados.values()]
    colores = ["tab:red", "tab:green"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    b1 = ax1.bar(etiquetas, valores, color=colores)
    ax1.bar_label(b1)
    ax1.set_ylabel("Valor total")
    ax1.set_title("Valor total obtenido")

    b2 = ax2.bar(etiquetas, pesos, color=colores)
    ax2.bar_label(b2)
    ax2.axhline(cap, color="black", linestyle="--", label=f"Capacidad = {cap}")
    ax2.set_ylabel("Capacidad usada")
    ax2.set_title("Capacidad usada")
    ax2.legend()

    fig.suptitle("Ejercicio 2: Greedy menor peso vs. mayor valor/peso")
    fig.tight_layout()

    if input("¿Guardar la gráfica? (s/n): ").strip().lower() == "s":
        plt.savefig(filename, dpi=150)
        print(f"Gráfica guardada en {filename}")
    if input("¿Mostrar la gráfica? (s/n): ").strip().lower() == "s":
        plt.show()
    plt.close()

if __name__ == "__main__":
    objetos = [("A", 45, 40), ("B", 65, 50), ("C", 80, 60)]
    cap = 130

    mostrar_tabla_objetos(objetos, cap)

    resultados = {
        "Menor peso": greedy(objetos, cap, obtener_peso),
        "Valor/peso": greedy(objetos, cap, obtener_ratio),
    }

    print("=" * 40)
    print("COMPARACIÓN")
    print("=" * 40)
    print(f"{'Método':12s} {'Objetos':10s} {'Peso usado':>10s} {'Valor':>6s}")
    for metodo, (v, w, llevar) in resultados.items():
        print(f"{metodo:12s} {str(llevar):10s} {w:>10d} {v:>6d}")
    print()

    plot_comparacion(resultados, cap)