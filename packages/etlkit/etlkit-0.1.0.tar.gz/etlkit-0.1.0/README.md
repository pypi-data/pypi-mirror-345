# ETLpip install setuptools wheel twine
 Pipeline

A simple Python package to extract, transform, and load data from various sources (CSV, API, SQLite) to different targets (CSV, JSON, SQLite).

## Features

- Extract from CSV, API, or SQLite DB
- Clean, aggregate, and format data
- Load to CSV, JSON, or SQLite

## Usage

```bash
elt-run --source-type csv --source-path data/input.csv --destination-path output/output.csv
