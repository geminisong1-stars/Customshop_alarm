"""seen.json (이미 본 상품 ID 목록) 저장/로드.

구조:
    {
        "musicforce": ["51368", "51367", ...],
        "buzzbee":    ["28109", ...],
        "digimart":   ["DS10570934", ...]
    }
"""
import json
import os


def load_seen(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seen(path, seen):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2, sort_keys=True)
