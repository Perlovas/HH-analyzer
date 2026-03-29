"""Очистка данных и выделение признаков для набора вакансий."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd


DEFAULT_SKILLS = [
    "python",
    "java",
    "javascript",
    "sql",
    "django",
    "flask",
    "fastapi",
    "spring",
    "pandas",
    "numpy",
    "git",
    "docker",
    "kubernetes",
    "linux",
    "airflow",
    "spark",
    "hadoop",
    "tableau",
    "power bi",
    "ml",
    "machine learning",
]


def _ensure_list(value) -> List:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def read_records(files: Sequence[Path]) -> pd.DataFrame:
    frames = []
    for file in files:
        if file.suffix.lower() == ".json":
            with open(file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            frames.append(pd.DataFrame(data))
        elif file.suffix.lower() == ".csv":
            frames.append(pd.read_csv(file))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def normalize_salaries(df: pd.DataFrame) -> pd.DataFrame:
    """Вычислить mid_salary и привести зарплаты к рублям.

    Правила:
    - если указана только одна граница, берём её как середину;
    - конвертируем по фиксированным курсам, чтобы не терять нерублёвые вакансии;
    - если валюта неизвестна — оставляем mid_salary пустым.
    """

    rates = {
        "rub": 1,
        "rur": 1,
        "usd": 90,
        "eur": 98,
        "kzt": 0.2,  # условный курс
        "uah": 2.4,  # условный курс
    }

    df = df.copy()
    df["currency"] = df["currency"].str.lower()

    # подготовка границ
    df["salary_from"] = df["salary_from"].fillna(df["salary_to"])
    df["salary_to"] = df["salary_to"].fillna(df["salary_from"])

    def to_mid(row):
        if pd.isna(row["salary_from"]) and pd.isna(row["salary_to"]):
            return None
        a = row["salary_from"] or row["salary_to"]
        b = row["salary_to"] or row["salary_from"]
        return (a + b) / 2

    df["mid_salary_src"] = df.apply(to_mid, axis=1)

    def to_rub(row):
        cur = row["currency"]
        if pd.isna(row["mid_salary_src"]):
            return None
        rate = rates.get(cur)
        if rate is None:
            return None
        return row["mid_salary_src"] * rate

    df["mid_salary"] = df.apply(to_rub, axis=1)
    return df


def extract_skills(df: pd.DataFrame, skills: Iterable[str] = DEFAULT_SKILLS) -> pd.DataFrame:
    """Сформировать колонку skills из key_skills и текста описания."""

    skills_lower = [s.lower() for s in skills]
    df = df.copy()
    df["description_lower"] = df["description"].fillna("").str.lower()

    # навыки из поля key_skills
    df["key_skills_norm"] = df["key_skills"].apply(
        lambda ks: list({(k or "").lower().strip() for k in (ks or []) if k})
    )

    for skill in skills_lower:
        df[f"skill_{skill}"] = df["description_lower"].str.contains(skill)

    def collect(row):
        from_desc = [skill for skill in skills_lower if row[f"skill_{skill}"]]
        merged = set(from_desc) | set(row["key_skills_norm"])
        return sorted(merged)

    df["skills"] = df.apply(collect, axis=1)
    return df.drop(columns=["description_lower"])


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset=["id"])


def save_dataset(df: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix == ".csv":
        df.to_csv(output, index=False)
    else:
        df.to_json(output, orient="records", force_ascii=False, indent=2)


__all__ = [
    "read_records",
    "normalize_salaries",
    "extract_skills",
    "deduplicate",
    "save_dataset",
    "DEFAULT_SKILLS",
]
