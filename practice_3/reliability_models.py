"""
Модуль математических моделей надёжности программного обеспечения.
Реализованы: Джелински-Моранды, Шумана, Нельсона-Коркорэна.
"""
import math
from typing import List, Tuple


class JelinskiMorandaModel:
    """
    Модель Джелински-Моранды.
    Допущения: интенсивность отказов пропорциональна числу оставшихся ошибок.
    """

    def __init__(self, N0: int, phi: float):
        """
        :param N0: начальное число ошибок
        :param phi: коэффициент пропорциональности (интенсивность обнаружения одной ошибки)
        """
        self.N0 = N0
        self.phi = phi

    def failure_intensity(self, i: int) -> float:
        """Интенсивность отказов после исправления i ошибок."""
        remaining = self.N0 - i
        if remaining < 0:
            raise ValueError("Число исправленных ошибок не может превышать начальное")
        return self.phi * remaining

    def reliability(self, t: float, i: int = 0) -> float:
        """Вероятность безотказной работы за время t после исправления i ошибок."""
        lam = self.failure_intensity(i)
        return math.exp(-lam * t)

    def mttf(self, i: int = 0) -> float:
        """Средняя наработка до отказа."""
        lam = self.failure_intensity(i)
        return 1.0 / lam if lam > 0 else float('inf')


class SchumanModel:
    """
    Модель Шумана.
    Допущения: интенсивность отказов пропорциональна удельному числу
    остаточных ошибок на одну машинную команду.
    """

    def __init__(self, I: int, E0: int, Ks: float):
        """
        :param I: общее число машинных команд
        :param E0: начальное число ошибок
        :param Ks: коэффициент пропорциональности
        """
        self.I = I
        self.E0 = E0
        self.Ks = Ks

    def residual_error_density(self, Ec: int) -> float:
        """Удельное число остаточных ошибок после исправления Ec ошибок."""
        return (self.E0 - Ec) / self.I

    def failure_intensity(self, Ec: int) -> float:
        """Интенсивность отказов при исправленных Ec ошибках."""
        return self.Ks * self.residual_error_density(Ec)

    def reliability(self, t: float, Ec: int = 0) -> float:
        """Вероятность безотказной работы."""
        lam = self.failure_intensity(Ec)
        return math.exp(-lam * t)

    def mttf(self, Ec: int = 0) -> float:
        """Средняя наработка до отказа."""
        lam = self.failure_intensity(Ec)
        return 1.0 / lam if lam > 0 else float('inf')

    @classmethod
    def estimate_parameters(
        cls, I: int,
        t1: float, t2: float,
        n1: int, n2: int,
        Ec1: int, Ec2: int
    ) -> Tuple[float, float]:
        """
        Оценка параметров E0 и Ks методом моментов.
        :param I: число команд
        :param t1, t2: периоды отладки
        :param n1, n2: число ошибок в периодах
        :param Ec1, Ec2: число исправленных ошибок к периодам
        :return: (E0, Ks)
        """
        gamma = (t1 * n2) / (t2 * n1) if n1 > 0 else 1.0
        E0 = I * (gamma * Ec1 - Ec2) / (gamma - 1) if gamma != 1 else 0
        Ks = n1 / (t1 * (E0 / I - Ec1 / I)) if E0 / I - Ec1 / I != 0 else 0
        return E0, Ks


class NelsonCorcoranModel:
    """
    Объединённая модель Нельсона-Коркорэна.
    Статическая модель надёжности, основанная на результатах прогонов.
    Часть Нельсона: разбиение области входных данных на подобласти
    с вероятностями P_i и долями отказов n_i/N_i.
    Расширение Коркорэна: учёт разных типов ошибок с вероятностями a_i.
    """

    def __init__(
        self,
        P: List[float],
        n: List[int],
        N: List[int],
        N0: int = None,
        Ni: List[int] = None,
        ai: List[float] = None
    ):
        """
        :param P: вероятности выбора подобластей (сумма = 1)
        :param n: число отказов в каждой подобласти
        :param N: число прогонов в каждой подобласти
        :param N0: число безотказных прогонов (для расширения Коркорэна)
        :param Ni: число ошибок i-го типа (для расширения Коркорэна)
        :param ai: вероятности выявления ошибок i-го типа (по умолчанию 0.5)
        """
        if abs(sum(P) - 1.0) > 1e-6:
            raise ValueError("Сумма вероятностей P должна быть равна 1")
        if len(P) != len(n) or len(P) != len(N):
            raise ValueError("Длины списков P, n, N должны совпадать")
        self.P = P
        self.n = n
        self.N = N
        self.N0 = N0 if N0 is not None else sum(N) - sum(n)
        self.Ni = Ni
        self.ai = ai if ai else ([0.5] * len(Ni) if Ni else [])

    def reliability_nelson(self) -> float:
        """Надёжность по части Нельсона (через подобласти)."""
        failure_prob = sum(
            (ni / Ni) * Pi
            for ni, Ni, Pi in zip(self.n, self.N, self.P)
        )
        return 1.0 - failure_prob

    def reliability_corcoran(self) -> float:
        """Надёжность по расширению Коркорэна (учёт типов ошибок)."""
        if not self.Ni:
            return self.reliability_simple()
        K = len(self.Ni)
        sum_term = sum(
            self.ai[i] * (self.Ni[i] - 1)
            for i in range(K)
            if self.Ni[i] > 0
        )
        N_total = self.N0 + sum(self.Ni)
        return (self.N0 + sum_term) / N_total

    def reliability_simple(self) -> float:
        """Упрощённая форма: 1 - n-/n, где n- = N - N0, n = N0 + sum(Ni)."""
        if self.Ni:
            n_failures = sum(self.Ni)
            n_total = self.N0 + n_failures
        else:
            n_failures = sum(self.n)
            n_total = sum(self.N)
        return 1.0 - n_failures / n_total

    def reliability(self) -> float:
        """Основная надёжность (по Нельсону)."""
        return self.reliability_nelson()


# =============================================================================
# ДЕМОНСТРАЦИЯ РАСЧЁТОВ
# =============================================================================
def demo_calculations():
    """Демонстрация расчётов по всем моделям."""
    print("=" * 70)
    print("РАСЧЁТ НАДЁЖНОСТИ ПО МОДЕЛЯМ")
    print("=" * 70)

    # --- Джелински-Моранды ---
    print("\n1. МОДЕЛЬ ДЖЕЛИНСКИ-МОРАНДЫ")
    jm = JelinskiMorandaModel(N0=50, phi=0.0001)
    print(f"   Интенсивность отказов (i=30): {jm.failure_intensity(30):.6f} отказов/час")
    print(f"   R(t=100) = {jm.reliability(100, i=30):.4f}")
    print(f"   MTTF = {jm.mttf(i=30):.2f} часов")

    # --- Шумана ---
    print("\n2. МОДЕЛЬ ШУМАНА")
    sch = SchumanModel(I=10000, E0=50, Ks=0.0001)
    print(f"   Удельное число остаточных ошибок: {sch.residual_error_density(30):.6f}")
    print(f"   Интенсивность отказов: {sch.failure_intensity(30):.8f}")
    print(f"   R(t=100) = {sch.reliability(100, Ec=30):.8f}")
    print(f"   MTTF = {sch.mttf(Ec=30):.0f} часов")

    # --- Нельсона-Коркорэна ---
    print("\n3. МОДЕЛЬ НЕЛЬСОНА-КОРКОРЭНА")
    nc = NelsonCorcoranModel(
        P=[0.6, 0.4],
        n=[5, 2],
        N=[100, 50],
        N0=970,
        Ni=[20, 10],
        ai=[0.7, 0.3]
    )
    print(f"   R (Нельсон, через подобласти) = {nc.reliability_nelson():.4f}")
    print(f"   R (Коркорэн, с типами ошибок) = {nc.reliability_corcoran():.4f}")
    print(f"   R (упрощённая) = {nc.reliability_simple():.4f}")


if __name__ == "__main__":
    demo_calculations()
