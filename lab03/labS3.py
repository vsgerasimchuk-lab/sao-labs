#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: O(n^2), лучший случай O(n)."""
    arr = list(a)  # копия, чтобы не менять вход
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return arr, comparisons, swaps

def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Ожидаемая сложность: O(n^2), лучший случай O(n)."""
    arr = list(a)
    comparisons = 0
    moves = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                moves += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
    return arr, comparisons, moves


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: O(n^2) на любом входе."""
    arr = list(a)
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
    return arr, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем O(n log n), в худшем O(n^2).
    Рандомизация делает худший случай маловероятным.
    """
    if rng is None:
        rng = random.Random()
    arr = list(a)
    _quick_sort_inplace(arr, 0, len(arr) - 1, rng)
    return arr


def _quick_sort_inplace(arr: list, lo: int, hi: int, rng: random.Random) -> None:
    """Рекурсивная часть QuickSort. Сортирует arr[lo..hi] на месте."""
    if lo >= hi:
        return
    pivot_idx = rng.randrange(lo, hi + 1)  # случайный опорный
    arr[lo], arr[pivot_idx] = arr[pivot_idx], arr[lo]  # ставим опорный в начало
    pivot = arr[lo]
    # Разделение (partition): элементы <= pivot — слева, > pivot — справа
    i = lo
    for j in range(lo + 1, hi + 1):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[lo], arr[i] = arr[i], arr[lo]  # ставим опорный на своё место
    _quick_sort_inplace(arr, lo, i - 1, rng)
    _quick_sort_inplace(arr, i + 1, hi, rng)


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны."""
    pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (2, "e")]
    print("\nДемонстрация стабильности:")
    print(f"  исходно:           {pairs}")
    print(f"  метки при ключе 1: b, d")
    print(f"  метки при ключе 2: a, c, e")

    # bubble — сравнение по ключу p[0]
    arr = list(pairs)
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):
            if arr[j][0] > arr[j + 1][0]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    print(f"  bubble_sort:       {[p[1] for p in arr]}")

    # insertion
    arr = list(pairs)
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j][0] > key[0]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    print(f"  insertion_sort:    {[p[1] for p in arr]}")

    # selection
    arr = list(pairs)
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j][0] < arr[min_idx][0]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
    print(f"  selection_sort:    {[p[1] for p in arr]}")

    # quick (in-place через вспомогательную функцию)
    arr = list(pairs)
    _quick_sort_pairs(arr, 0, len(arr) - 1, random.Random(0))
    print(f"  quick_sort:        {[p[1] for p in arr]}")

def _quick_sort_pairs(arr: list, lo: int, hi: int, rng: random.Random) -> None:
    """QuickSort по ключу p[0] для пар. Сортирует arr на месте."""
    if lo >= hi:
        return
    pivot_idx = rng.randrange(lo, hi + 1)
    arr[lo], arr[pivot_idx] = arr[pivot_idx], arr[lo]
    pivot = arr[lo][0]
    i = lo
    for j in range(lo + 1, hi + 1):
        if arr[j][0] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[lo], arr[i] = arr[i], arr[lo]
    _quick_sort_pairs(arr, lo, i - 1, rng)
    _quick_sort_pairs(arr, i + 1, hi, rng)


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def check_algorithm(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: получено {res}")
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_counters() -> None:
    """Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе."""
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10,
           f"selection_sort: неверный счётчик сравнений — {comparisons}, ожидалось 10")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_algorithm(fn)) for name, fn in ALGORITHMS.items()]
    checks.append(("счётчики", check_counters))
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
        _, comps, _ = bubble_sort([1, 2, 3, 4, 5])
        expect(comps == 4,
               f"bubble_sort на отсортированном: {comps}, ожидалось 4")

        _, comps, _ = insertion_sort([5, 4, 3, 2, 1])
        expect(comps == 10,
               f"insertion_sort на обратном: {comps}, ожидалось 10")

        _, comps, _ = selection_sort([1, 2, 3, 4, 5])
        expect(comps == 10,
               f"selection_sort на отсортированном: {comps}, ожидалось 10")
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
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                print(f"  n={n:>7}  вход={cls:<13} t={bench(fn, data):.6f} c")

def plot_results(seed: int) -> None:
    """Log-log графики: время от размера для всех сортировок и классов входов."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — графики пропущены")
        return

    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(20, 4.5), sharey=True)
    for ax, (name, fn, sizes) in zip(axes, plans):
        for cls in ("упорядоченный", "случайный", "обратный"):
            ns = []
            ts = []
            for n in sizes:
                data = make_inputs(n, seed)[cls]
                ns.append(n)
                ts.append(bench(fn, data))
            ax.plot(ns, ts, marker="o", label=cls)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("размер n")
        ax.set_title(name)
        ax.grid(True, which="both", linewidth=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("время, с")
    fig.tight_layout()
    path = "lab03_sorting.png"
    fig.savefig(path, dpi=150)
    print(f"\nГрафик сохранён: {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)
    plot_results(seed)


if __name__ == "__main__":
    main()
