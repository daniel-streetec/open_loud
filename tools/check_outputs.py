"""Audit generated constraints, required parameter metadata and expected BOM sums."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    checks = []
    data = json.loads((ROOT / "data/parameters.json").read_text(encoding="utf-8"))

    def walk(value, path=""):
        if isinstance(value, dict):
            if "value" in value:
                assert all(k in value for k in ("unit", "source", "status", "uncertainty")), path
            else:
                for k, entry in value.items():
                    walk(entry, path + "." + k)

    walk(data)
    checks.append("All numerical parameter records have units, source, status and uncertainty")
    manifest = json.loads((ROOT / "results/manifest.json").read_text(encoding="utf-8"))
    for path, digest in manifest["source_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    checks.append("Source hashes match generated results")
    n = 0
    with (ROOT / "results/acoustics.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            n += 1
            base = row["concept"].split("-")[0]
            driver = data["drivers"][data["concepts"][base]["driver"]]
            assert float(row["x_peak_at_limit_mm"]) <= driver["Xmax"]["value"] * 1000 + 1e-9
            assert float(row["port_peak_at_limit_m_s"]) <= data["model"]["port_peak_limit"]["value"] + 1e-9
            assert float(row["limit_Vrms"]) <= float(row["rail_limit_Vrms"]) + 1e-9
            assert float(row["limit_Vrms"]) <= float(row["board_cap_Vrms"]) + 1e-9
            assert float(row["real_power_at_limit_W"]) >= float(row["copper_power_at_limit_W"]) - 1e-9
            assert all(math.isfinite(float(v)) for k, v in row.items() if k not in ("concept", "first_limit") and v != "")
    assert n == 3 * data["model"]["points"]["value"]
    checks.append(f"{n} frequency rows finite and within selected excursion/port/voltage limits; passive power balance plausible")
    summary = json.loads((ROOT / "results/summary.json").read_text(encoding="utf-8"))
    for concept, expected in (("A0", 368.34), ("A1", 445.23)):
        assert abs(summary["costs"][concept]["material"] - expected) < 1e-8
    checks.append("Structured BOM reproduces report material totals A0 368.34 / A1 445.23 EUR")
    output = {"status": "passed", "checks": checks, "scope": "mathematical and generated-file checks only; no physical validation"}
    (ROOT / "results/validation.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print("\n".join(checks))


if __name__ == "__main__":
    main()
