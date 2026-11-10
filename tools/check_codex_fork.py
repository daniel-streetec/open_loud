"""Actual minimal, read-only CLI fork smoke test; consumes one model response."""
import json,os,shutil,subprocess
from pathlib import Path
from resume_after_reset import command
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'.tools/overnight';out.mkdir(parents=True,exist_ok=True)
    args=command(shutil.which('codex'),os.environ['CODEX_THREAD_ID'],out/'fork-smoke-last.txt')
    args=[('sandbox_mode="read-only"' if arg.startswith('sandbox_mode=') else arg) for arg in args]
    args.append('--ephemeral')
    result=subprocess.run(args,input='Dies ist nur ein Wiederanlauf-Test. Antworte exakt OPEN_LOUD_FORK_OK. Keine Werkzeuge verwenden, keine Dateien lesen oder schreiben, keine Projektarbeit starten.',
        text=True,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120,cwd=ROOT)
    (out/'fork-smoke.jsonl').write_text(result.stdout,encoding='utf-8')
    final=(out/'fork-smoke-last.txt').read_text(encoding='utf-8').strip() if (out/'fork-smoke-last.txt').exists() else None
    report=dict(exit_code=result.returncode,final_message=final,passed=result.returncode==0 and final=='OPEN_LOUD_FORK_OK')
    (out/'fork-smoke-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report));assert report['passed'],result.stdout[-1500:]
if __name__=='__main__':main()
