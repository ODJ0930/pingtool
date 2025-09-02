#!/usr/bin/env python3
"""Ping global IPs by country and compute average latency and packet loss."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

DATA_URL = "https://public-dns.info/nameservers.json"
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_FILE = DATA_DIR / "nameservers.json"
SAMPLE_FILE = DATA_DIR / "nameservers.sample.json"

# Minimal Chinese aliases for country codes
CHINESE_ALIASES = {
    "中国": "CN",
    "美国": "US",
    "日本": "JP",
    "韩国": "KR",
    "德国": "DE",
    "英国": "GB",
    "法国": "FR",
    "俄罗斯": "RU",
    "加拿大": "CA",
    "澳大利亚": "AU",
    "印度": "IN",
    "巴西": "BR",
    "新加坡": "SG",
    "香港": "HK",
}


def download_dataset() -> Path:
    """Attempt to download the IP dataset. Return path to dataset."""
    DATA_DIR.mkdir(exist_ok=True)
    if DATA_FILE.exists():
        return DATA_FILE
    try:
        import urllib.request

        with urllib.request.urlopen(DATA_URL, timeout=10) as resp:  # type: ignore
            content = resp.read()
        with open(DATA_FILE, "wb") as f:
            f.write(content)
        return DATA_FILE
    except Exception:
        return SAMPLE_FILE


def load_dataset() -> List[dict]:
    """Load dataset as list of dicts."""
    path = download_dataset()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_country_maps(dataset: List[dict]) -> Tuple[dict, dict]:
    """Return (code_to_name, english_name_to_code)."""
    code_to_name = {}
    english_to_code = {}
    for entry in dataset:
        code = entry.get("country_id")
        name = entry.get("country", "").lower()
        if code:
            code_to_name.setdefault(code, name)
            if name:
                english_to_code[name] = code
    return code_to_name, english_to_code


def normalize_country(query: str, english_to_code: dict) -> str:
    q = query.strip().lower()
    if len(q) == 2 and q.upper() in english_to_code.values():
        return q.upper()
    if q in CHINESE_ALIASES:
        return CHINESE_ALIASES[q]
    if q in english_to_code:
        return english_to_code[q]
    raise ValueError(f"Unknown country: {query}")


def progress_bar(iterable: Iterable, total: int) -> Iterable:
    for idx, item in enumerate(iterable, 1):
        bar_len = 40
        filled = int(bar_len * idx / total)
        bar = "#" * filled + "-" * (bar_len - filled)
        print(f"\r[{bar}] {idx}/{total}", end="", flush=True)
        yield item
    print()


def ping(ip: str, packets: int) -> Tuple[float, float]:
    """Return (packet_loss_percent, avg_latency_ms)."""
    try:
        out = subprocess.check_output(
            ["ping", "-c", str(packets), "-W", "2", ip],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        out = e.output
    loss_match = re.search(r"(\d+(?:\.\d+)?)% packet loss", out)
    loss = float(loss_match.group(1)) if loss_match else 100.0
    rtt_match = re.search(r"= [^/]+/([^/]+)/", out)
    avg = float(rtt_match.group(1)) if rtt_match else float("nan")
    return loss, avg


def main() -> None:
    parser = argparse.ArgumentParser(description="Ping IPs by country")
    parser.add_argument("-c", "--country", help="Country name or code")
    parser.add_argument("--count", type=int, default=5, help="Number of IPs to ping")
    parser.add_argument("--packets", type=int, default=4, help="Packets per ping")
    args = parser.parse_args()

    dataset = load_dataset()
    code_to_name, english_to_code = build_country_maps(dataset)

    if args.country:
        country_query = args.country
    else:
        country_query = input("Enter country (e.g., China/cn/中国): ")
    try:
        code = normalize_country(country_query, english_to_code)
    except ValueError as e:
        print(e)
        sys.exit(1)

    name = code_to_name.get(code, code)
    ips = [d["ip"] for d in dataset if d.get("country_id") == code][: args.count]
    if not ips:
        print(f"No IPs found for {name}")
        sys.exit(1)

    losses: List[float] = []
    avgs: List[float] = []
    for ip in progress_bar(ips, len(ips)):
        loss, avg = ping(ip, args.packets)
        losses.append(loss)
        if not (avg != avg):  # check for NaN
            avgs.append(avg)

    avg_loss = sum(losses) / len(losses)
    avg_latency = sum(avgs) / len(avgs) if avgs else float("nan")
    print(f"Average latency for {name}: {avg_latency:.2f} ms")
    print(f"Average packet loss: {avg_loss:.2f}%")


if __name__ == "__main__":
    main()
