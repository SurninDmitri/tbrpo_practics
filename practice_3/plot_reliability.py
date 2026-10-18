"""
Построение графиков зависимости надёжности ПО от времени наработки.
Использует модели из reliability_models.py.
Сохраняет график в reliability_curves.png.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reliability_models import JelinskiMorandaModel, SchumanModel, NelsonCorcoranModel


def plot_reliability_curves(
    output_file: str = "reliability_curves.png",
    show: bool = False
):
    """Построение графиков зависимости надёжности от времени."""
    t = np.linspace(1, 500, 100)

    # Джелински-Моранды
    jm = JelinskiMorandaModel(N0=50, phi=0.0001)
    R_jm = [jm.reliability(ti, i=30) for ti in t]

    # Шумана
    sch = SchumanModel(I=10000, E0=50, Ks=0.0001)
    R_sch = [sch.reliability(ti, Ec=30) for ti in t]

    # Нельсона-Коркорэна (статическая модель, значения не зависят от времени)
    nc = NelsonCorcoranModel(
        P=[0.6, 0.4],
        n=[5, 2],
        N=[100, 50],
        N0=970,
        Ni=[20, 10],
        ai=[0.7, 0.3]
    )

    plt.figure(figsize=(10, 6))
    plt.plot(t, R_jm, 'b-', label='Джелински-Моранды', linewidth=2)
    plt.plot(t, R_sch, 'r--', label='Шумана', linewidth=2)
    plt.axhline(y=nc.reliability_nelson(), color='g', linestyle='-.',
                label=f'Нельсон (R={nc.reliability_nelson():.3f})', linewidth=1.5)
    plt.axhline(y=nc.reliability_corcoran(), color='m', linestyle='-.',
                label=f'Коркорэн (R={nc.reliability_corcoran():.3f})', linewidth=1.5)
    plt.axhline(y=0.95, color='gray', linestyle=':', label='Целевой уровень R=0.95')
    plt.xlabel('Время наработки, часы')
    plt.ylabel('Вероятность безотказной работы R(t)')
    plt.title('Сравнение моделей надёжности ПО')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    if show:
        plt.show()
    plt.close()
    print(f"График сохранён: {output_file}")


if __name__ == "__main__":
    plot_reliability_curves()
