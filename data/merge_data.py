from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Tuple


DEFAULT_LEFT = Path(__file__).with_name("owid-energy-data.csv")
DEFAULT_RIGHT = Path(__file__).with_name("global-data-on-sustainable-energy (1).csv")
DEFAULT_OUTPUT = Path(__file__).with_name("merged-energy-data.csv")

LEFT_KEY_CANDIDATES = ("country", "entity")
RIGHT_KEY_CANDIDATES = ("country", "entity")
YEAR_KEY_CANDIDATES = ("year",)


def _normalize_header(header: str) -> str:
	normalized = [character.lower() if character.isalnum() else "_" for character in header.strip()]
	cleaned = "".join(normalized)
	while "__" in cleaned:
		cleaned = cleaned.replace("__", "_")
	return cleaned.strip("_")


def _find_value(row: Mapping[str, str], candidates: Iterable[str]) -> str:
	lookup = {column.strip().lower(): column for column in row.keys()}
	for candidate in candidates:
		column_name = lookup.get(candidate.lower())
		if column_name is None:
			continue
		value = (row.get(column_name) or "").strip()
		if value:
			return value
	return ""


def _read_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
	with path.open("r", encoding="utf-8-sig", newline="") as file_handle:
		reader = csv.DictReader(file_handle)
		headers = reader.fieldnames or []
		rows = [dict(row) for row in reader]
	return headers, rows


def _build_index(
	rows: Iterable[Mapping[str, str]],
	country_candidates: Iterable[str],
	year_candidates: Iterable[str],
) -> Dict[Tuple[str, str], Mapping[str, str]]:
	indexed_rows: Dict[Tuple[str, str], Mapping[str, str]] = {}
	for row in rows:
		country = _find_value(row, country_candidates)
		year = _find_value(row, year_candidates)
		if not country or not year:
			continue
		indexed_rows[(country.casefold(), year)] = row
	return indexed_rows


def _prefixed_columns(headers: List[str], prefix: str, key_columns: Iterable[str]) -> List[str]:
	key_set = {column.strip().lower() for column in key_columns}
	columns: List[str] = []
	for header in headers:
		if header.strip().lower() in key_set:
			continue
		columns.append(f"{prefix}{_normalize_header(header)}")
	return columns


def merge_datasets(left_path: Path, right_path: Path, output_path: Path) -> Path:
	left_headers, left_rows = _read_rows(left_path)
	right_headers, right_rows = _read_rows(right_path)

	left_index = _build_index(left_rows, LEFT_KEY_CANDIDATES, YEAR_KEY_CANDIDATES)
	right_index = _build_index(right_rows, RIGHT_KEY_CANDIDATES, YEAR_KEY_CANDIDATES)

	all_keys = sorted(
		set(left_index.keys()) | set(right_index.keys()),
		key=lambda item: (item[0], int(item[1]) if item[1].isdigit() else item[1]),
	)

	left_output_columns = _prefixed_columns(left_headers, "owid_", ("country", "entity", "year"))
	right_output_columns = _prefixed_columns(right_headers, "sustainable_", ("country", "entity", "year"))
	fieldnames = ["country", "year", *left_output_columns, *right_output_columns]

	output_path.parent.mkdir(parents=True, exist_ok=True)
	with output_path.open("w", encoding="utf-8", newline="") as file_handle:
		writer = csv.DictWriter(file_handle, fieldnames=fieldnames, extrasaction="ignore")
		writer.writeheader()

		for country_key, year in all_keys:
			merged_row: Dict[str, str] = {column: "" for column in fieldnames}
			left_row = left_index.get((country_key, year))
			right_row = right_index.get((country_key, year))
			source_row = left_row or right_row or {}

			merged_row["country"] = source_row.get("country", "") or source_row.get("Entity", "") or source_row.get("entity", "")
			merged_row["year"] = year

			if left_row is not None:
				for header in left_headers:
					if header.strip().lower() in {"country", "entity", "year"}:
						continue
					merged_row[f"owid_{_normalize_header(header)}"] = (left_row.get(header) or "").strip()

			if right_row is not None:
				for header in right_headers:
					if header.strip().lower() in {"country", "entity", "year"}:
						continue
					merged_row[f"sustainable_{_normalize_header(header)}"] = (right_row.get(header) or "").strip()

			writer.writerow(merged_row)

	return output_path


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Merge the TB4 energy datasets by country and year.")
	parser.add_argument("--left", type=Path, default=DEFAULT_LEFT, help="Path to the OWID CSV file.")
	parser.add_argument("--right", type=Path, default=DEFAULT_RIGHT, help="Path to the sustainable energy CSV file.")
	parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path for the merged CSV output.")
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	output_path = merge_datasets(args.left, args.right, args.output)
	print(f"Merged file written to: {output_path}")


if __name__ == "__main__":
	main()
