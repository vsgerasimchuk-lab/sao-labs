#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.

    Стабильность: при равенстве ключей элемент из left идёт раньше.
    Ожидаемая сложность: O(n), где n = len(left) + len(right).
    """
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    # дописываем остаткиыыыыы
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список. Ожидаемая сложность: O(n log n)."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max].

    Схема: массив счётчиков -> префиксные суммы -> расстановка с конца.
    Ожидаемые время и память: O(n + k), где k = key_max + 1.
    """
    if not a:
        return []
    counts = [0] * (key_max + 1)
    for x in a:
        counts[x] += 1
    # префиксные суммы: counts[i] = сколько элементов <= i
    for i in range(1, key_max + 1):
        counts[i] += counts[i - 1]
    result = [0] * len(a)
    # расстановка с конца — для устойчивости
    for i in range(len(a) - 1, -1, -1):
        x = a[i]
        counts[x] -= 1
        result[counts[x]] = x
    return result


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.

    Ожидаемая сложность: O(d · (n + 10)), где d — число разрядов.
    """
    if not a:
        return []
    result = list(a)
    max_val = max(result)
    exp = 1
    while max_val // exp > 0:
        # counting sort по цифре (x // exp) % 10
        counts = [0] * 10
        for x in result:
            digit = (x // exp) % 10
            counts[digit] += 1
        for i in range(1, 10):
            counts[i] += counts[i - 1]
        temp = [0] * len(result)
        for i in range(len(result) - 1, -1, -1):
            digit = (result[i] // exp) % 10
            counts[digit] -= 1
            temp[counts[digit]] = result[i]
        result = temp
        exp *= 10
    return result


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest == i:
            break
        a[i], a[largest] = a[largest], a[i]
        i = largest


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте. Сложность: O(n log n)."""
    n = len(a)
    # 1. Построение max-кучи: снизу вверх просеиваем
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    # 2. Извлечение максимумов
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]   # максимум в конец
        sift_down(a, 0, i)         # восстанавливаем кучу в a[0:i]


def quick_sort(a: list[int]) -> list[int]:
    """QuickSort с рандомизацией опорного элемента (из ЛР 3)."""

    def _sort(arr, lo, hi):
        if lo >= hi:
            return

        pivot_idx = random.randrange(lo, hi + 1)
        arr[lo], arr[pivot_idx] = arr[pivot_idx], arr[lo]
        pivot = arr[lo]

        # Трёхпутевое разбиение: защита от дубликатов
        lt = lo
        gt = hi
        i = lo
        while i <= gt:
            if arr[i] < pivot:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > pivot:
                arr[i], arr[gt] = arr[gt], arr[i]
                gt -= 1
            else:
                i += 1

        _sort(arr, lo, lt - 1)
        _sort(arr, gt + 1, hi)

    result = list(a)
    _sort(result, 0, len(result) - 1)
    return result


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


# Каждая функция возвращает отсортированный список; ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [0],                   # нулевой ключ
        [5, 5, 5],             # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    # Случайные тесты: инвариант перестановки + сверка с эталоном
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, порядковый номер): эталон sorted() стабилен,
    поэтому при равных ключах порядок номеров обязан совпасть."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    # Собственные проверки инвариантов
    try:
        # Свойство кучи после построения (только фаза 1)
        arr = [3, 1, 5, 2, 4, 0, 7]
        n = len(arr)
        for i in range(n // 2 - 1, -1, -1):
            sift_down(arr, i, n)
        for i in range(n):
            left, right = 2 * i + 1, 2 * i + 2
            if left < n:
                expect(arr[i] >= arr[left], f"куча: a[{i}] < левого потомка")
            if right < n:
                expect(arr[i] >= arr[right], f"куча: a[{i}] < правого потомка")

        # Radix — устойчивость по разрядам на парах (ключ, порядок)
        pairs = [(12, 0), (21, 1), (12, 2), (21, 3)]
        sorted_keys = radix_sort_lsd([p[0] for p in pairs])
        expect(sorted_keys == [12, 12, 21, 21],
               f"radix_sort: {sorted_keys}, ожидалось [12, 12, 21, 21]")
    except SelfCheckError as err:
        print(f"  собственные проверки: ОШИБКА — {err}")
        failed += 1
    else:
        print("  собственные проверки: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл (обсудить в отчёте)


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.

    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", quick_sort),
        ("sorted() (эталон)", sorted),
    ]
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    # счётчики размера ~10^9 не помещаются в память — граница
                    # применимости counting; зафиксировать в таблице свойств
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                print(f"    {algo_name:>18}: t = {bench(fn, data):.6f} c")
    # TODO: построить log-log графики (matplotlib) по каждому распределению;
    # TODO: заполнить таблицу свойств: время (лучший/средний/худший),
    #       память, стабильность, ограничения — для всех шести сортировок;
    # TODO: объяснить расхождения замеров с асимптотикой в отчёте.


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)
    plot_results(seed)


def plot_results(seed: int) -> None:
    """Log-log графики: время от размера для всех сортировок и распределений."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — графики пропущены")
        return

    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", quick_sort),
        ("sorted()", sorted),
    ]

    distributions = ["random_wide", "random_small", "sorted", "reversed", "almost_sorted"]

    fig, axes = plt.subplots(1, 5, figsize=(25, 5), sharey=False)

    for ax, dist_name in zip(axes, distributions):
        for algo_name, fn in algorithms:
            ns = []
            ts = []
            rng_local = random.Random(seed)  # одинаковые данные для всех
            for n in SIZES:
                data = make_datasets(rng_local, n)[dist_name]
                # пропуск counting для random_wide
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    continue
                ns.append(n)
                ts.append(bench(fn, data))
            if ns:
                ax.plot(ns, ts, marker="o", label=algo_name)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("размер n")
        ax.set_title(dist_name)
        ax.grid(True, which="both", linewidth=0.3)
        ax.legend(fontsize=7)

    axes[0].set_ylabel("время, с")
    fig.tight_layout()
    path = "lab04_sorting.png"
    fig.savefig(path, dpi=150)
    print(f"\nГрафик сохранён: {path}")

if __name__ == "__main__":
    main()
