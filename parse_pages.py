import re
import json
import csv
import unicodedata
from pathlib import Path
from collections import defaultdict

PAGES_DIR = Path("pages")
OUTPUT_DIR = Path("artifacts")
OUTPUT_DIR.mkdir(exist_ok=True)

LINK_RE = re.compile(r"\[\[(.+?)\]\]")
HASHTAG_RE = re.compile(r"#(?P<tag>[\wÁ-Üá-ü\-]+)")
YEAR_RANGE_RE = re.compile(r"(\d{4})\s*[-–]\s*(\d{4})")


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def clean_label(label: str) -> str:
    text = label.strip()
    if text.startswith("[[") and text.endswith("]]" ):
        text = text[2:-2]
    if text.startswith("#"):
        text = text[1:]
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -\t")


def split_period(label: str):
    match = YEAR_RANGE_RE.search(label)
    if not match:
        return label.strip(), None
    period = f"{match.group(1)}-{match.group(2)}"
    base = YEAR_RANGE_RE.sub("", label).strip()
    base = re.sub(r"\s+", " ", base)
    return base, period


def normalize_id(label: str) -> str:
    clean = clean_label(label)
    base, period = split_period(clean)
    ascii_base = strip_accents(base).lower()
    ascii_base = re.sub(r"[^a-z0-9]+", " ", ascii_base).strip()
    ascii_base = re.sub(r"\s+", " ", ascii_base)
    if period:
        return f"{ascii_base}|{period}"
    return ascii_base


def parse_file(path: Path):
    title = path.stem
    with path.open("r", encoding="utf-8") as fh:
        lines = [line.rstrip("\n") for line in fh]
    bullets = []
    for line in lines:
        if line.startswith("- "):
            bullets.append(line[2:].strip())
        elif line.startswith("-"):
            bullets.append(line[1:].strip())
    links = []
    hashtags = []
    for bullet in bullets:
        links.extend(LINK_RE.findall(bullet))
        hashtags.extend(tag for tag in HASHTAG_RE.findall(bullet))
    return {
        "title": title,
        "bullets": bullets,
        "links": links,
        "hashtags": hashtags,
    }


def build_nodes(pages_data):
    nodes = {}
    duplicates = defaultdict(list)
    for entry in pages_data:
        norm_id = normalize_id(entry["title"])
        base, period = split_period(clean_label(entry["title"]))
        node = {
            "id": norm_id,
            "label": entry["title"],
            "base_name": base,
            "period": period,
            "file": entry["file"],
            "links": entry["links"],
            "hashtags": entry["hashtags"],
        }
        if norm_id in nodes:
            duplicates[norm_id].append(entry["title"])
        else:
            nodes[norm_id] = node
    return nodes, duplicates


def add_hashtag_nodes(pages_data, nodes, duplicates):
    for entry in pages_data:
        for tag in entry["hashtags"]:
            norm_id = normalize_id(tag)
            base, period = split_period(clean_label(tag))
            label = f"#{clean_label(tag)}"
            node = {
                "id": norm_id,
                "label": label,
                "base_name": base,
                "period": period,
                "file": None,
                "links": [],
                "hashtags": [],
            }
            if norm_id in nodes:
                duplicates[norm_id].append(label)
            else:
                nodes[norm_id] = node


def build_edges(nodes, pages_data):
    edges = []
    broken_links = []
    for entry in pages_data:
        source_id = normalize_id(entry["title"])
        for bullet in entry["bullets"]:
            for link in LINK_RE.findall(bullet):
                target_id = normalize_id(link)
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "context": bullet,
                })
                if target_id not in nodes:
                    broken_links.append({
                        "source": entry["title"],
                        "target": link,
                        "normalized_target": target_id,
                        "file": entry["file"],
                    })
            for tag in HASHTAG_RE.findall(bullet):
                normalized_tag = normalize_id(tag)
                edges.append({
                    "source": source_id,
                    "target": normalized_tag,
                    "context": bullet,
                    "type": "hashtag",
                })
                if normalized_tag not in nodes:
                    broken_links.append({
                        "source": entry["title"],
                        "target": f"#{tag}",
                        "normalized_target": normalized_tag,
                        "file": entry["file"],
                    })
    return edges, broken_links


def write_json(path: Path, data):
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def write_csv(path: Path, data, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def main():
    pages_data = []
    for path in sorted(PAGES_DIR.glob("*.md")):
        parsed = parse_file(path)
        parsed["file"] = str(path)
        pages_data.append(parsed)

    nodes, duplicates = build_nodes(pages_data)
    add_hashtag_nodes(pages_data, nodes, duplicates)
    edges, broken_links = build_edges(nodes, pages_data)

    write_json(OUTPUT_DIR / "nodes.json", list(nodes.values()))
    write_json(OUTPUT_DIR / "edges.json", edges)
    write_json(OUTPUT_DIR / "duplicates.json", duplicates)
    write_json(OUTPUT_DIR / "broken_links.json", broken_links)

    write_csv(OUTPUT_DIR / "nodes.csv", list(nodes.values()), [
        "id", "label", "base_name", "period", "file", "links", "hashtags"
    ])
    write_csv(OUTPUT_DIR / "edges.csv", edges, [
        "source", "target", "context", "type"
    ])

    summary = {
        "pages": len(pages_data),
        "nodes": len(nodes),
        "edges": len(edges),
        "duplicates_found": len(duplicates),
        "broken_links": len(broken_links),
    }
    write_json(OUTPUT_DIR / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
