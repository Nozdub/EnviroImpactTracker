import os
import json


def load_benchmark_data():
    # Get base directory (project root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Path to /app/data/benchmark_data.json
    filepath = os.path.join(base_dir, "data", "benchmark_data.json")

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)
