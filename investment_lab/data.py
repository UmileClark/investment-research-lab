"""Frozen inputs, strict as-of selection and adjusted-price archive bridging."""
from pathlib import Path
from datetime import date
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / "data" / name).read_text())


def settings():
    return json.loads((ROOT / "config" / "research.json").read_text())


def verify_inputs():
    manifest = read("manifest.json")
    for name, expected in manifest["hashes"].items():
        actual = hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Frozen input changed: {name}")
    return manifest


class Market:
    def __init__(self):
        self.book = read("book.json")
        self.symbols = [h[0] for h in self.book["holdings"] if h[0] != "CASH"]
        self.currency = {h[0]: h[4] for h in self.book["holdings"]}
        self.weights = np.array([h[3] / 100 for h in self.book["holdings"] if h[0] != "CASH"])
        self.pre = read("training_prices.json")
        self.post = read("historical_prices.json")
        self.current = read("current_book.json")
        self.bridge = {}
        self.combined = {}
        for symbol in self.symbols + ["EURUSD=X"]:
            old = self.row(self.pre, symbol, "2024-09-27", exact=True)
            new = self.row(self.post, symbol, "2024-09-27", exact=True)
            factor = new["adjusted"] / old["adjusted"]
            self.bridge[symbol] = factor
            # Adjusted histories can be rebased after later distributions.
            # Rescale the older archive at a common date; never splice levels raw.
            rows = {r["date"]: {**r, "adjusted": r["adjusted"] * factor}
                    for r in self.pre[symbol]["rows"] if r["date"] <= "2024-09-27"}
            rows.update({r["date"]: r for r in self.post[symbol]["rows"] if r["date"] >= "2024-09-27"})
            self.combined[symbol] = {"rows": sorted(rows.values(), key=lambda r: r["date"])}

    @staticmethod
    def row(archive, symbol, day, exact=False):
        rows = [r for r in archive[symbol]["rows"] if r["date"] <= day]
        if not rows:
            raise ValueError(f"No quote at or before {day}: {symbol}")
        r = rows[-1]
        if exact and r["date"] != day:
            raise ValueError(f"Missing exact quote: {symbol} {day}")
        if (date.fromisoformat(day) - date.fromisoformat(r["date"])).days > 5:
            raise ValueError(f"Stale quote: {symbol} {day}")
        if not np.isfinite(r["adjusted"]) or r["adjusted"] <= 0 or r["close"] <= 0:
            raise ValueError(f"Invalid price: {symbol} {day}")
        return r

    def eur_price(self, archive, symbol, day, exact=False):
        r = self.row(archive, symbol, day, exact)
        fx = 1 if self.currency[symbol] == "EUR" else 1 / self.row(archive, "EURUSD=X", day, exact)["close"]
        return r["adjusted"] * fx

    def panel(self, archive, start, end, symbols=None):
        symbols = self.symbols if symbols is None else symbols
        common = set.intersection(*[{r["date"] for r in archive[s]["rows"]}
                                   for s in symbols + ["EURUSD=X"]])
        dates = sorted(d for d in common if start <= d <= end and date.fromisoformat(d).weekday() < 5)
        if len(dates) < 2:
            raise ValueError("Too few common observations")
        prices = np.array([[self.eur_price(archive, s, d, exact=True) for s in symbols] for d in dates])
        return dates, prices

    def training(self):
        return self.panel(self.pre, "2021-09-27", settings()["training_end"])
