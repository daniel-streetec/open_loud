"""Generate all E01 outputs from data/. Run from any working directory."""
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import values, response, limits, crossing, port_geometry, input_power, constant_power_pack

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"


def write_csv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pick(item, key, concept, default=None):
    entry = item.get(key, default)
    return entry.get(concept) if isinstance(entry, dict) else entry


def main():
    OUT.mkdir(exist_ok=True)
    data = json.loads((ROOT / "data/parameters.json").read_text(encoding="utf-8"))
    components = json.loads((ROOT / "data/components.json").read_text(encoding="utf-8"))
    env, model, energy, mech = (values(data[g]) for g in ("environment", "model", "energy", "mechanical"))
    count = int(model["points"])
    fs = [model["f_min"] * (model["f_max"] / model["f_min"]) ** (i / (count - 1)) for i in range(count)]
    all_rows, summaries, diagnostics, sensitivity, bom_rows, energy_rows, pack_rows = [], [], {}, [], [], [], []
    costs = {}
    for concept, config in data["concepts"].items():
        driver = values(data["drivers"][config["driver"]])
        case = values(config)
        cms = 1 / ((2 * math.pi * driver["Fs"]) ** 2 * driver["Mms"])
        vas = env["rho"] * env["c"] ** 2 * driver["Sd"] ** 2 * cms
        qts = 2 * math.pi * driver["Fs"] * driver["Mms"] / (driver["Rms"] + driver["Bl"] ** 2 / driver["Re"])
        diagnostics[concept] = {"derived_Vas_l": vas * 1000, "listed_Vas_l": driver["Vas"] * 1000,
                                "Vas_deviation_percent": 100 * (vas / driver["Vas"] - 1),
                                "derived_Qts": qts, "listed_Qts": driver["Qts"]}
        for sealed in (False, True) if concept == "A0" else (False,):
            label = concept + ("-sealed-control" if sealed else "")
            responses = [response(f, driver, case, env, model, sealed=sealed) for f in fs]
            norm = sum(r["spl_1V"] for f, r in zip(fs, responses) if model["norm_low"] <= f <= model["norm_high"]) / sum(model["norm_low"] <= f <= model["norm_high"] for f in fs)
            relative = [r["spl_1V"] - norm for r in responses]
            for f, r, rel in zip(fs, responses, relative):
                v, first, bounds = limits(r, driver, case, model)
                uncapped, _, _ = limits(r, driver, case, model, capped=False)
                all_rows.append({"concept": label, "frequency_Hz": f, "response_dB": rel,
                    "SPL_1Vrms_2pi_1m_dB": r["spl_1V"], "SPL_limit_2pi_1m_dB": r["spl_1V"] + 20 * math.log10(v),
                    "limit_Vrms": v, "first_limit": first, "rail_limit_Vrms": bounds["rail"],
                    "board_cap_Vrms": case["amp_rms_cap"], "hub_limit_Vrms": bounds["excursion"],
                    "port_limit_Vrms": bounds["port"] if math.isfinite(bounds["port"]) else "",
                    "thermal_proxy_limit_Vrms": bounds["copper_proxy"],
                    "uncapped_SPL_dB": r["spl_1V"] + 20 * math.log10(uncapped),
                    "x_peak_at_limit_mm": r["x_peak"] * v * 1000,
                    "port_peak_at_limit_m_s": r["port_peak"] * v,
                    "x_peak_at_rail_mm": r["x_peak"] * bounds["rail"] * 1000,
                    "port_peak_at_rail_m_s": r["port_peak"] * bounds["rail"],
                    "real_power_at_limit_W": r["power_real"] * v ** 2,
                    "copper_power_at_limit_W": r["power_copper"] * v ** 2,
                    "current_at_limit_Arms": abs(r["current"]) * v,
                    "Z_abs_ohm": abs(r["impedance"]), "Z_phase_deg": math.degrees(math.atan2(r["impedance"].imag, r["impedance"].real))})
            effective, physical = (0, 0) if sealed else port_geometry(case, env, model)
            summary = {"concept": label, **{f"F{n}_Hz": crossing(fs, relative, -n, model["norm_low"]) for n in (3, 6, 10)},
                       "port_effective_m": effective, "port_physical_m": physical}
            for f in (30, 40, 50, 63, 80, 100):
                r = response(f, driver, case, env, model, sealed=sealed)
                v, first, _ = limits(r, driver, case, model)
                summary[f"SPL_{f}Hz_dB"] = r["spl_1V"] + 20 * math.log10(v)
                summary[f"limit_{f}Hz"] = first
            summaries.append(summary)
        for ql in (4, 7, 12):
            for rail in ((15, 18, 21) if concept == "A0" else (18, 23.5)):
                alternative_model = dict(model, ql=ql)
                alternative_case = dict(case, rail=rail)
                rs = [response(f, driver, alternative_case, env, alternative_model) for f in fs]
                band = [r["spl_1V"] for f, r in zip(fs, rs) if model["norm_low"] <= f <= model["norm_high"]]
                ys = [r["spl_1V"] - sum(band) / len(band) for r in rs]
                r50 = response(50, driver, alternative_case, env, alternative_model)
                v50, _, _ = limits(r50, driver, alternative_case, alternative_model)
                sensitivity.append({"concept": concept, "Ql": ql, "rail_V": rail, "F6_Hz": crossing(fs, ys, -6, model["norm_low"]), "SPL_50Hz_dB": r50["spl_1V"] + 20 * math.log10(v50)})
        costs[concept] = {"material": 0, "tools": 0, "allowance": 0}
        for item in components["items"]:
            if concept not in item.get("applies_to", ["A0", "A1"]):
                continue
            price = pick(item, "price", concept)
            total = item["quantity"] * price
            group = "tools" if item.get("cost_group") == "reusable_tool" else "material"
            costs[concept][group] += total
            if item["price_status"] == "allowance":
                costs[concept]["allowance"] += total
            mass = driver["mass"] if item.get("mass_parameter") else pick(item, "mass_kg", concept)
            bom_rows.append({"concept": concept, "id": item["id"], "manufacturer": pick(item, "manufacturer", concept),
                "mpn": pick(item, "mpn", concept), "quantity": item["quantity"], "purchase_unit": item["unit"],
                "unit_price_EUR_gross": price, "line_total_EUR_gross": round(total, 2),
                "date": components["default_price_date"], "source": pick(item, "source", concept),
                "price_status": item["price_status"], "mass_kg_each": mass,
                "alternative": item.get("alternative"), "approval": components["default_approval"], "note": item.get("note", "")})
        for profile, entry in data["energy"]["profiles"].items():
            low, high = entry["value"]
            pmin = input_power(low, energy, config["power_path"] == "boost", False)
            pmax = input_power(high, energy, config["power_path"] == "boost", True)
            energy_rows.append({"concept": concept, "profile": profile, "audio_mean_low_W": low, "audio_mean_high_W": high,
                "pack_low_W": pmin, "pack_high_W": pmax, "runtime_low_h": energy["usable_low"] / pmax,
                "runtime_high_h": energy["usable_high"] / pmin, "status": "scenario_not_measurement"})
        for voc in (energy["voc_nominal"], energy["voc_low"]):
            for resistance in (energy["pack_resistance_low"], energy["pack_resistance_high"]):
                p = input_power(energy["peak_audio"], energy, config["power_path"] == "boost", True)
                solution = constant_power_pack(voc, resistance, p)
                voltage, current = solution if solution else (None, None)
                pack_rows.append({"concept": concept, "Voc_V": voc, "R_pack_ohm": resistance, "stress_power_W": p,
                    "terminal_V": voltage, "current_A": current, "below_trial_UVLO": voltage is None or voltage < energy["uvlo_trial"],
                    "status": "hypothetical_R_not_BMS_or_fuse_rating"})
    write_csv("acoustics.csv", all_rows)
    write_csv("sensitivity.csv", sensitivity)
    write_csv("bom.csv", bom_rows)
    write_csv("energy.csv", energy_rows)
    write_csv("pack_stress.csv", pack_rows)
    inner = math.prod(mech[k] - 2 * mech["wall"] for k in ("height", "width", "depth"))
    shell = math.prod(mech[k] for k in ("height", "width", "depth")) - inner
    output = {"revision": data["revision"], "model_status": "simulation_not_measurement", "acoustics": summaries,
              "TS_consistency": diagnostics, "costs": costs,
              "envelope": {"inner_geometric_l": inner * 1000, "shell_mass_before_cutouts_kg": [shell * mech["density_low"], shell * mech["density_high"]]}}
    (OUT / "summary.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# Erster Konzeptvergleich E01", "", "Generiert mit `python simulation/run.py`. Lineares LF-Modell, keine Messung, keine Bau-/DSP-Freigabe.", "",
        "| Konzept | F3 / F6 / F10 Hz | SPL-Grenze 50 / 63 Hz, dB, 2π/1m | Port effektiv / physisch cm |",
        "|---|---|---|---|"]
    for row in summaries:
        lines.append(f"| {row['concept']} | {row['F3_Hz']:.1f} / {row['F6_Hz']:.1f} / {row['F10_Hz']:.1f} | {row['SPL_50Hz_dB']:.1f} / {row['SPL_63Hz_dB']:.1f} | {100*row['port_effective_m']:.1f} / {100*row['port_physical_m']:.1f} |")
    lines += ["", "A1 ist auf 14,142 Vrms gekappt. CSV enthält zusätzlich das ungekappte Berichtsszenario und jede einzelne frequenzabhängige Grenze. Pn dient nur als unvalidierter Kupferverlust-Proxy; kein thermischer Nachweis.", "",
        "| Konzept | Material / erster Bau inkl. Programmer EUR | davon Planbeträge EUR | Masse laut Bericht kg |",
        "|---|---|---|---|"]
    for concept, cost in costs.items():
        conf = values(data["concepts"][concept])
        lines.append(f"| {concept} | {cost['material']:.2f} / {cost['material']+cost['tools']:.2f} | {cost['allowance']:.2f} | {conf['mass_low']:.0f}–{conf['mass_high']:.0f}, unbestätigt |")
    lines += ["", "Kosten und Tragemassen dieser Tabelle sind E01-Referenzans?tze. Verst?rkte E03-Mechanik ist darin nicht vollst?ndig kalkuliert; siehe data/mechanical_hardware.json und hardware/mechanical/README.md."]
    dimensions = '/'.join(f"{mech[k]*1000:.0f}" for k in ("height", "width", "depth"))
    lines += ["", f"Beide nutzen vorläufig H/B/T {dimensions} mm. Geometrisch innen {inner*1000:.2f} l vor Einbauten; reine Hülle vor Ausschnitten {shell*mech['density_low']:.2f}–{shell*mech['density_high']:.2f} kg. Keine vollständige Verdrängungs- oder Schwerpunktbilanz.", "",
        "| Konzept / Lastprofil | mittlere Akkuaufnahme W | Laufzeitbereich h |", "|---|---|---|"]
    for row in energy_rows:
        lines.append(f"| {row['concept']} / {row['profile']} | {row['pack_low_W']:.1f}–{row['pack_high_W']:.1f} | {row['runtime_low_h']:.1f}–{row['runtime_high_h']:.1f} |")
    lines += ["", "Laufzeiten setzen 58–65 Wh nutzbar voraus. Keine Entladekurve, Zelltemperatur oder Alterung modelliert. A1-Wandler-Idle 0,3 W ist eine zusätzliche ungemessene E01-Annahme. Gleiche mittlere elektrische Audioleistung bedeutet nicht gleichen akustischen Nutzpegel.", "",
        "A0 vermeidet den Wandler und bleibt erste Referenz, überschreitet aber den 300-EUR-Materialansatz. A1 bietet mehr modellierten Tiefbass, gefährdet das 11-kg-Ziel und benötigt Wandler-/Packprüfung. Beide benötigen gemessene Polaren, DSP-Schutz, thermische Prüfung und konkrete Schutzbauteile. Keine endgültige Konzeptauswahl.", "",
        "Pack-Spitzenrechnung: `pack_stress.csv` löst eine hypothetische Konstantleistungsbelastung mit 0,05/0,2 Ohm Packwiderstand. Unterspannungsfälle sind Ausfallindikatoren; 15 V ist kein freigegebener Zellschutzwert. 75 W Audio ist nur ein Versorgungs-Stressfall, keine sichere HF-Dauerleistung."]
    (OUT / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sources = [ROOT / "data/parameters.json", ROOT / "data/components.json", ROOT / "simulation/model.py", Path(__file__), ROOT / "docs/research/OPEN_LOUD_Forschungsbericht_Phase_1.pdf"]
    manifest = {"python": platform.python_version(), "source_sha256": {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Generated acoustics, sensitivity, BOM, energy, pack stress, comparison, summary and manifest in results/")


if __name__ == "__main__":
    main()
