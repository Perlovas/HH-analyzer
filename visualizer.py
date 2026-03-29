"""Утилиты визуализации для аналитики вакансий."""

from __future__ import annotations

from pathlib import Path

import matplotlib

# Без GUI-бекенда, чтобы не было предупреждений в потоках Flask.
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set(style="whitegrid")


def _ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def plot_salary_distribution(series, output: Path, title: str = "Распределение зарплат"):
    _ensure_output_dir(output)
    plt.figure(figsize=(8, 5))
    sns.histplot(series.dropna(), bins=20, kde=True)
    plt.title(title)
    plt.xlabel("Зарплата, руб")
    plt.ylabel("Количество вакансий")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def plot_top_skills(series, output: Path, title: str = "ТОП навыков"):
    _ensure_output_dir(output)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=series.values, y=series.index)
    plt.title(title)
    plt.xlabel("Количество вакансий")
    plt.ylabel("Навык")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def plot_top_cities(series, output: Path, title: str = "ТОП городов"):
    _ensure_output_dir(output)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=series.values, y=series.index)
    plt.title(title)
    plt.xlabel("Количество вакансий")
    plt.ylabel("Город")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def plot_publications_over_time(series, output: Path, title: str = "Динамика публикаций"):
    _ensure_output_dir(output)
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=series.index, y=series.values)
    plt.title(title)
    plt.xlabel("Дата")
    plt.ylabel("Количество вакансий")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


__all__ = [
    "plot_salary_distribution",
    "plot_top_skills",
    "plot_top_cities",
    "plot_publications_over_time",
]
