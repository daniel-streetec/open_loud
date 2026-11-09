"""Run checks in order, abort on failure; verify deterministic regeneration."""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def hashes():
    return {str(p.relative_to(ROOT/'results')): hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "results").rglob('*') if p.is_file()}


if __name__ == "__main__":
    run("-m", "unittest", "discover", "-s", "tests", "-v")
    run("simulation/run.py")
    run("tools/check_outputs.py")
    run("tools/generate_wiring.py")
    run("tools/generate_wiring_bom.py")
    run("tools/compare_festival_energy.py")
    before = hashes()
    run("simulation/run.py")
    run("tools/check_outputs.py")
    run("tools/generate_wiring.py")
    run("tools/generate_wiring_bom.py")
    run("tools/compare_festival_energy.py")
    if hashes() != before:
        raise RuntimeError("Outputs changed between identical runs")
    print("Reproduction passed; all generated files byte-identical across two runs.")
