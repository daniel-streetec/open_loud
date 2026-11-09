"""Linear LF lumped-element model; SI, RMS electrical/velocity, peak limits."""
import cmath
import math


def values(group):
    return {k: v["value"] for k, v in group.items() if isinstance(v, dict) and "value" in v}


def db(x, reference=1):
    return 20 * math.log10(max(abs(x), 1e-30) / reference)


def response(f, driver, case, env, model, sealed=False, inductance=0):
    """Response for 1 Vrms. Box loss flow is dissipative, not radiated."""
    w = 2 * math.pi * f
    cms = 1 / ((2 * math.pi * driver["Fs"]) ** 2 * driver["Mms"])
    cab = case["Vb"] / (env["rho"] * env["c"] ** 2)
    admittance = 1j * w * cab
    zp = None
    if not sealed:
        wb = 2 * math.pi * case["Fb"]
        port_mass = 1 / (wb ** 2 * cab)
        zp = port_mass * (wb / model["qp"] + 1j * w)
        admittance += wb * cab / model["ql"] + 1 / zp
    zb = 1 / admittance
    zm = driver["Rms"] + 1j * (w * driver["Mms"] - 1 / (w * cms)) + driver["Sd"] ** 2 * zb
    ze = driver["Re"] + 1j * w * inductance + driver["Bl"] ** 2 / zm
    current = 1 / ze
    velocity = driver["Bl"] * current / zm
    uc = driver["Sd"] * velocity
    up = -uc * zb / zp if zp is not None else 0j
    pressure = 1j * env["rho"] * w * (uc + up) / (2 * math.pi * env["distance"])
    return {
        "pressure": pressure, "current": current, "velocity": velocity,
        "cone_flow": uc, "port_flow": up,
        "x_peak": math.sqrt(2) * abs(velocity) / w,
        "port_peak": math.sqrt(2) * abs(up) / case["port_area"] if not sealed else 0,
        "power_real": current.real, "power_copper": abs(current) ** 2 * driver["Re"],
        "spl_1V": db(pressure, env["p0"]), "impedance": ze,
    }


def limits(r, driver, case, model, capped=True):
    limits_ = {
        "rail": model["rail_fraction"] * case["rail"] / math.sqrt(2),
        "excursion": driver["Xmax"] / r["x_peak"],
        "copper_proxy": math.sqrt(driver["Pn"] / r["power_copper"]),
        "port": model["port_peak_limit"] / r["port_peak"] if r["port_peak"] else math.inf,
    }
    if capped:
        limits_["board_cap"] = case["amp_rms_cap"]
    first = min(limits_, key=limits_.get)
    return limits_[first], first, limits_


def crossing(frequencies, levels, target, ceiling=180):
    """Last upward crossing below reference band; absent crossings return null."""
    found = None
    for f0, f1, y0, y1 in zip(frequencies, frequencies[1:], levels, levels[1:]):
        if f1 <= ceiling and y0 <= target < y1:
            found = f0 + (f1 - f0) * (target - y0) / (y1 - y0)
    return found


def port_geometry(case, env, model):
    cab = case["Vb"] / (env["rho"] * env["c"] ** 2)
    mass = 1 / ((2 * math.pi * case["Fb"]) ** 2 * cab)
    effective = mass * case["port_area"] / env["rho"]
    physical = effective - model["end_correction"] * 2 * math.sqrt(case["port_area"] / math.pi)
    return effective, physical


def input_power(audio, energy, boosted, conservative):
    eta = energy["eta_low" if conservative else "eta_high"]
    aux = energy["aux_high" if conservative else "aux_low"]
    power = energy["idle"] + aux + audio / eta
    if boosted:
        power = power / energy["boost_eta_low" if conservative else "boost_eta_high"] + energy["boost_idle"]
    return power


def constant_power_pack(voc, resistance, power):
    """Stable high-voltage solution of P = I (Voc - I R). None = no DC solution."""
    if resistance == 0:
        return voc, power / voc
    discriminant = voc ** 2 - 4 * resistance * power
    if discriminant < 0:
        return None
    terminal = (voc + math.sqrt(discriminant)) / 2
    return terminal, power / terminal
