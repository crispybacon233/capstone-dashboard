import csv
from pathlib import Path


def load_keyword_data(csv_path: str = "src/keywords.csv") -> tuple[list[str], list[tuple[str, str]]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Keyword CSV not found: {path}")

    keywords: list[str] = []
    word_pairs: list[tuple[str, str]] = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required_columns = {"kind", "keyword", "word1", "word2"}
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                "Invalid keyword CSV schema. Expected columns: kind,keyword,word1,word2"
            )

        for row in reader:
            kind = (row.get("kind") or "").strip().lower()

            if kind == "keyword":
                keyword = (row.get("keyword") or "").strip()
                if keyword:
                    keywords.append(keyword)
                continue

            if kind == "pair":
                word1 = (row.get("word1") or "").strip()
                word2 = (row.get("word2") or "").strip()
                if word1 and word2:
                    word_pairs.append((word1, word2))

    return keywords, word_pairs
